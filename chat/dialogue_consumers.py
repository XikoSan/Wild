import json
import re
from datetime import datetime

import bleach
import pytz
import redis
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from django.utils import timezone

from chat.models.stickers_ownership import StickersOwnership
from chat.models.sticker import Sticker
from player.player import Player
from chat.models.messages.chat_members import ChatMembers
import logging
from chat.models.messages.message_block import MessageBlock
from chat.models.messages.chat import Chat


def _get_player(account):
    return Player.objects.select_related('account').get(account=account)


def _get_sticker_packs(pk):
    # return StickersOwnership.objects.filter(owner__pk=pk).first().pk
    return StickersOwnership.objects.filter(owner__pk=pk).values_list('pack__pk', flat=True)


def _get_player_pk(pk):
    return Player.get_instance(pk=pk)


def _get_user(pk):
    return User.objects.prefetch_related('groups').get(pk=pk)


def _get_groups(user):
    return list(user.groups.all().values_list('name', flat=True))


# проверить, есть ли игрок в этом чате
def _check_has_chat(pk, chat_pk):
    if ChatMembers.objects.filter(chat__pk=chat_pk, player__pk=pk).exists():
        return True
    else:
        return False


def _check_has_pack(message, packs):
    if int(message.split('_')[0]) in packs:
        return Sticker.objects.get(pk=int(message.split('_')[1])).image.url
    else:
        return False


def _delete_message(chat_id, counter):
    r = redis.StrictRedis(host='redis', port=6379, db=0)

    r.zremrangebyscore(f'dialogue_{chat_id}', counter, counter)

def _get_awa(image):
    return image.url


def get_last_id_from_db(chat_id):
    ret_id = None

    block = MessageBlock.objects.filter(chat=int(chat_id)).order_by('-date').first()
    if not block:
        return ret_id

    db_dump = eval(block.messages)

    ret_id = db_dump[-1][1]

    return ret_id


def mark_read_in_db(chat_id, counter):
    was_found = False
    excluded_blocks_pk = []

    while not was_found:
        block = MessageBlock.objects.filter(chat=int(chat_id)).exclude(pk__in=excluded_blocks_pk).order_by('-date').first()
        if not block:
            break

        db_dump = eval(block.messages)

        updated_tuple = [(json.loads(message[0]), message[1]) if message[1] == float(counter) else message for message in
                         db_dump]

        updated_tuple = [
            (json.dumps({**data, "read": True}, indent=2, default=str), score) if score == float(counter) else (
            message[0], message[1]) for message in updated_tuple for data, score in [message]]

        block.messages = str(updated_tuple)
        block.save()

        for message in updated_tuple:
            if message[1] == float(counter):
                was_found = True
                break

        excluded_blocks_pk.append(block.pk)


def _mark_as_read(chat_id, counter):

    r = redis.StrictRedis(host='redis', port=6379, db=0)
    # проверяем наличие такого rank в ОЗУ
    if not r.zrangebyscore(f'dialogue_{chat_id}', counter, counter):
        return mark_read_in_db(chat_id, counter)

    # получаем сообщение в его текущем состоянии
    message = r.zrangebyscore(f'dialogue_{chat_id}', counter, counter)[0]
    # удаляем из ОЗУ
    r.zremrangebyscore(f'dialogue_{chat_id}', counter, counter)

    # преобразуем в dict
    message = json.loads(message)
    # меняем признак "прочитано"
    message['read'] = True

    # собираем в json заново
    o_json = json.dumps(message, indent=2, default=str)
    # вставляем на место удалённого
    r.zadd(f'dialogue_{chat_id}', {o_json: counter})


def _append_message(chat_id, author, text):

    message = {
                'author': author.pk,
               'content': text,
               'dtime': str(datetime.now().timestamp()).split('.')[0],
                'read': False
               }

    redis_last_message_index = 0

    # logger = logging.getLogger(__name__)

    # try:

    r = redis.StrictRedis(host='redis', port=6379, db=0)

    redis_list = r.zrevrange(f'dialogue_{chat_id}', 0, 0, withscores=True)

    # logger.debug(chat_id)
    # logger.debug(redis_list)

    # если в редисе ничего нет, то либо чат новый, либо всё в БД
    if redis_list:
        redis_last_message_index = redis_list[0][1]
    # подглядим в БД
    else:
        redis_last_message_index = get_last_id_from_db(chat_id)

    o_json = json.dumps(message, indent=2, default=str)

    r.zadd(f'dialogue_{chat_id}', {o_json: int(redis_last_message_index) + 1})

    count = r.zcard(f'dialogue_{chat_id}')

    # logger.debug(f'count: {count}')
    from player.logs.print_log import log
    log(count)

    # сохраняем каждые 50 сообщений
    if count > 49:
        pass
        redis_list = r.zrevrange(f'dialogue_{chat_id}', 0, -1, withscores=True)
        redis_list.reverse()

        block = MessageBlock(
            chat=Chat.objects.get(pk=str(chat_id)),
            messages=str(redis_list)
        )
        block.save()

        r.zremrangebyrank(f'dialogue_{chat_id}', 0, -1)

    # except Exception as e:
    #
    #     logger.exception('Произошла нештатная ситуация:')

    return int(redis_last_message_index) + 1


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.player = await sync_to_async(_get_player, thread_sensitive=True)(account=self.scope["user"])
        self.sticker_packs = await sync_to_async(_get_sticker_packs, thread_sensitive=True)(pk=self.player.pk)
        user = await sync_to_async(_get_user, thread_sensitive=True)(pk=self.player.account.pk)
        groups = await sync_to_async(_get_groups, thread_sensitive=True)(user=user)

        if not self.player.chat_ban \
                or 'chat_moderator' in groups:

            if 'chat_moderator' in groups:
                self.moderator = True
            else:
                self.moderator = False

            # logger = logging.getLogger(__name__)
            # logger.debug(self.scope['url_route']['kwargs']['room_name'])

            self.room_name = self.scope['url_route']['kwargs']['room_name']

            self.room_group_name = 'dialogue_%s' % self.room_name

            if await sync_to_async(_check_has_chat, thread_sensitive=True)(
                                                                            pk=self.player.pk,
                                                                            chat_pk=int(self.room_name)
                                                                           ):

                # Join room group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )

                await self.accept()

            else:
                self.close()

        else:
            self.close()

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        message = None
        if 'message' in text_data_json:
            message = bleach.clean(text_data_json['message'][:500], strip=True)

        sticker = None
        if 'sticker' in text_data_json:
            sticker = bleach.clean(text_data_json['sticker'], strip=True)

        if (not message or not re.search('[^\s]', message)) and (not sticker):
            return

        sticker_only = False
        if not message and sticker:
            message = sticker
            sticker_only = True

        if sticker_only:
            link = await sync_to_async(_check_has_pack, thread_sensitive=True)(message=message,
                                                                                   packs=self.sticker_packs)

            if link:
                message = '<img src="' + link + '" width="250" height="250" style="pointer-events: none;">'

        counter = None

        if not message == 'was_read':
            counter = await sync_to_async(_append_message, thread_sensitive=True)(
                                                                                    chat_id=self.room_name,
                                                                                    author=self.player,
                                                                                    text=message
                                                                                  )

        destination = ''

        logger = logging.getLogger(__name__)
        try:
            # если это увед о прочтении, и есть необходимые признаки
            if message == 'was_read' and text_data_json['counter']:
            # отметим прочитанным
                counter = text_data_json['counter']
                await sync_to_async(_mark_as_read, thread_sensitive=True)(
                                                                            chat_id=int(self.room_name),
                                                                            counter=counter
                                                                          )

            image_url = '/static/img/nopic.svg'
            if self.player.image:
                image_url = self.player.image.url

            if counter:
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'id': self.player.pk,
                        'image': image_url,
                        'nickname': self.player.nickname,
                        'message': message,
                        'destination': destination,
                        'counter': counter
                    }
                )
        except Exception as e:
            logger.exception('Произошла нештатная ситуация:')

    # Receive message from room group
    async def chat_message(self, event):

        message = event['message']
        id = event['id']
        image = event['image']
        nickname = event['nickname']
        counter = event['counter']

        if message == 'ban_chat':
            if event['destination'] == self.player.pk:
                self.disconnect()

        else:

            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
                'time': datetime.now().astimezone(pytz.timezone(self.player.time_zone)).strftime("%d.%m.%y %H:%M"),
                'id': id,
                'image': image,
                'nickname': nickname,
                'counter': counter,
            }))