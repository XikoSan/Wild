import bleach
import json
import pytz
import re
import redis
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import pgettext

from chat.models.sticker import Sticker
from chat.models.stickers_ownership import StickersOwnership
from player.player import Player


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


def _set_player_banned(pk):
    Player.objects.filter(pk=pk).update(chat_ban=True)


def _check_has_pack(message, packs):
    if int(message.split('_')[0]) in packs:
        sticker = Sticker.objects.get(pk=int(message.split('_')[1]))
        return sticker.image.url, sticker.description
    else:
        return False, None


def _delete_message(chat_id, counter):
    r = redis.StrictRedis(host='redis', port=6379, db=0)

    appendix = ''

    if chat_id not in ['ru', 'be', 'uk', 'hy']:
        # appendix = f'_{chat_id}'
        appendix = f'_en'
    else:
        appendix = f'_ru'

    r.zremrangebyscore('chat' + appendix, counter, counter)


# def _get_last_10_messages(chat_id):
#     chat, created = Chat.objects.get_or_create(chat_id=chat_id)
#     messages = []
#     for message in reversed(
#             chat.messages.order_by('-timestamp').exclude(content='ban_chat')[:10].values('author__pk', 'author__image',
#                                                                                          'content',
#                                                                                          'timestamp')):
#         messages.append(message)
#     return messages


def _get_awa(image):
    return image.url


def _get_blocked_txt():
    return pgettext('chat', 'Успешно заблокирован')


def _append_message(chat_id, author, text):
    message = {'author': author.pk,
               'content': text,
               'dtime': str(datetime.now().timestamp()).split('.')[0]
               }

    r = redis.StrictRedis(host='redis', port=6379, db=0)

    counter = 0
    appendix = ''

    if chat_id not in ['ru', 'be', 'uk', 'hy']:
        # appendix = f'_{chat_id}'
        appendix = f'_en'
    else:
        appendix = f'_ru'

    if r.hlen('counter' + appendix) > 0:
        counter = r.hget('counter' + appendix, 'counter')

    r.hset('counter' + appendix, 'counter', int(counter) + 1)

    o_json = json.dumps(message, indent=2, default=str)

    r.zadd('chat' + appendix, {o_json: int(counter) + 1})

    count = r.zcard("chat" + appendix)

    if count > 150:
        r.zremrangebyrank('chat' + appendix, 0, 0)

    return int(counter) + 1


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

            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = 'chat_%s' % self.room_name

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

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

        image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        if message and \
                message[:4] == 'http' and \
                any(message.lower().endswith(extension) for extension in image_extensions):
            message = '<img src="' + message + '">'

        sticker_only = False
        if not message and sticker:
            message = sticker
            sticker_only = True

        if sticker_only:
            link, desc = await sync_to_async(_check_has_pack, thread_sensitive=True)(message=message,
                                                                                     packs=self.sticker_packs)

            if link:
                # if desc in ['padoru', ]:
                if False:
                    desc = '\'' + desc + '\''
                    message = '<img src="' + link + '" width="250" height="250" onclick="audio_play(' + desc + ')" style="cursor: pointer">'
                else:
                    message = '<img src="' + link + '" width="250" height="250" style="pointer-events: none;">'

        counter = await sync_to_async(_append_message, thread_sensitive=True)(chat_id=self.room_name,
                                                                              author=self.player,
                                                                              text=message)

        destination = ''

        if (message == 'ban_chat' or message == 'delete_message') \
                and not self.moderator:
            pass

        else:
            if message == 'delete_message' \
                    and text_data_json['counter']:
                counter = int(text_data_json['counter'])
                await sync_to_async(_delete_message, thread_sensitive=True)(chat_id=self.room_name, counter=counter)

            else:
                if message == 'ban_chat' \
                        and text_data_json['destination']:
                    destination = text_data_json['destination']
                    await sync_to_async(_set_player_banned, thread_sensitive=True)(pk=destination)

                image_url = '/static/img/nopic.svg'
                if self.player.image:
                    image_url = self.player.image_75.url

                if len(self.player.nickname) > 25:
                    nickname = f'{self.player.nickname[:25]}...'
                else:
                    nickname = self.player.nickname

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'id': self.player.pk,
                        'image': image_url,
                        'nickname': nickname,
                        'message': message,
                        'destination': destination,
                        'counter': counter
                    }
                )

            if message == 'ban_chat' \
                    and text_data_json['destination']:

                banned_player = await sync_to_async(_get_player_pk, thread_sensitive=True)(pk=destination)

                banned_image_url = '/static/img/nopic.svg'
                if banned_player.image:
                    banned_image_url = banned_player.image.url

                # Сообщить об успешном бане
                await self.send(text_data=json.dumps({
                    'message': await sync_to_async(_get_blocked_txt, thread_sensitive=True)(),
                    'nickname': 'Chat system',
                    'time': datetime.now().time().strftime("%H:%M"),
                    'id': banned_player.pk,
                    'image': banned_image_url,
                }))

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
                'time': datetime.now().astimezone(pytz.timezone(self.player.time_zone)).time().strftime("%H:%M"),
                'id': id,
                'image': image,
                'nickname': nickname,
                'counter': counter,
            }))
