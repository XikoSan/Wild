import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from channels.db import database_sync_to_async
from player.player import Player
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from .models import Chat, Message
from player.logs.print_log import log
from django.utils.timezone import make_aware
import bleach
import pytz


def _get_player(account):
    return Player.objects.select_related('account').get(account=account)


def _get_player_pk(pk):
    return Player.objects.get(pk=pk)


def _get_user(pk):
    return User.objects.prefetch_related('groups').get(pk=pk)


def _get_groups(user):
    return list(user.groups.all().values_list('name', flat=True))


def _set_player_banned(pk):
    Player.objects.filter(pk=pk).update(chat_ban=True)


def _get_last_10_messages(chat_id):
    chat, created = Chat.objects.get_or_create(chat_id=chat_id)
    messages = []
    for message in reversed(
            chat.messages.order_by('-timestamp').exclude(content='ban_chat')[:10].values('author__pk', 'author__image', 'content',
                                                                   'timestamp')):
        messages.append(message)
    return messages


def _get_awa(image):
    return image.url


def _append_message(chat_id, author, text):
    message = Message.objects.create(
        author=author,
        content=text)
    chat, created = Chat.objects.get_or_create(chat_id=chat_id)
    chat.messages.add(message)
    chat.save()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.player = await sync_to_async(_get_player, thread_sensitive=True)(account=self.scope["user"])
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

            messages = await sync_to_async(_get_last_10_messages, thread_sensitive=True)(chat_id=self.room_name)

            for message in messages:

                if message['content'] == 'ban_chat':
                    continue

                image_url = '/static/img/nopic.png'
                if message['author__image']:
                    image_url = '/media/' + message['author__image']

                # Send message to WebSocket
                await self.send(text_data=json.dumps({
                    'message': message['content'],
                    'time': message['timestamp'].astimezone(pytz.timezone(self.player.time_zone)).time().strftime(
                        "%H:%M"),
                    'id': message['author__pk'],
                    'image': image_url,
                    # 'image': await sync_to_async(_get_image_url, thread_sensitive=True)(image=message['author__image']),
                }))

        else:
            self.close()

    # async def disconnect(self, code):
    #     # Leave room group
    #     await self.channel_layer.group_discard(
    #         self.room_group_name,
    #         self.channel_name
    #     )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        destination = ''

        await sync_to_async(_append_message, thread_sensitive=True)(chat_id=self.room_name,
                                                                    author=self.player,
                                                                    text=bleach.clean(message))

        if message == 'ban_chat' \
                and not self.moderator:
            pass

        else:
            if message == 'ban_chat'\
                    and text_data_json['destination']:
                destination = text_data_json['destination']
                await sync_to_async(_set_player_banned, thread_sensitive=True)(pk=destination)

            image_url = '/static/img/nopic.png'
            if self.player.image:
                image_url = self.player.image.url

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'id': self.player.pk,
                    'image': image_url,
                    'nickname': self.player.nickname,
                    'message': message,
                    'destination': destination
                }
            )

            if message == 'ban_chat'\
                    and text_data_json['destination']:

                banned_player = await sync_to_async(_get_player_pk, thread_sensitive=True)(pk=destination)

                banned_image_url = '/static/img/nopic.png'
                if banned_player.image:
                    banned_image_url = banned_player.image.url

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'id': banned_player.pk,
                        'image': banned_image_url,
                        'nickname': banned_player.nickname,
                        'message': 'Пользователь заблокирован модератором ' + self.player.nickname,
                    }
                )

    # Receive message from room group
    async def chat_message(self, event):

        message = event['message']
        id = event['id']
        image = event['image']
        nickname = event['nickname']

        if message == 'ban_chat':
            if event['destination'] == self.player.pk:

                image_url = '/static/img/nopic.png'
                if self.player.image:
                    image_url = self.player.image.url

                # Send message to WebSocket
                await self.send(text_data=json.dumps({
                    'message': 'Вы заблокированы модератором ' + nickname,
                    'time': datetime.now().time().strftime("%H:%M"),
                    'id': self.player.pk,
                    'image': image_url,
                }))
                # # Send message to room group
                # await self.channel_layer.group_send(
                #     self.room_group_name,
                #     {
                #         'type': 'chat_message',
                #         'id': self.player.pk,
                #         'image': image_url,
                #         'nickname': self.player.nickname,
                #         'message': 'Пользователь заблокирован модератором ' + nickname,
                #     }
                # )

                self.disconnect()

        else:

            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': bleach.clean(message),
                'time': datetime.now().astimezone(pytz.timezone(self.player.time_zone)).time().strftime("%H:%M"),
                'id': id,
                'image': image,
                'nickname': nickname,
            }))
