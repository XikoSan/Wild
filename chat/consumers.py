import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

from player.player import Player
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

def _get_player(account):
    return Player.objects.select_related('account').get(account=account)

def _get_user(pk):
    return User.objects.prefetch_related('groups').get(pk=pk)

def _get_groups(user):
    return list(user.groups.all().values_list('name', flat=True))

def _set_player_banned(pk):
    Player.objects.filter(pk=pk).update(chat_ban=True)

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.player = await sync_to_async(_get_player, thread_sensitive=True)(account=self.scope["user"])
        user = await sync_to_async(_get_user, thread_sensitive=True)(pk=self.player.account.pk)
        groups = await sync_to_async(_get_groups, thread_sensitive=True)(user=user)

        if not self.player.chat_ban\
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
            self.disconnect()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        destination = ''

        if message == 'disconnect' \
                and not self.moderator:
             pass

        else:
            if message == 'disconnect':
                destination = text_data_json['destination']

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'id': self.player.pk,
                    'image': self.player.image.url,
                    'nickname': self.player.nickname,
                    'message': message,
                    'destination': destination
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        id = event['id']
        image = event['image']
        nickname = event['nickname']

        if message == 'disconnect':
            if event['destination'] == self.player.pk:

                await sync_to_async(_set_player_banned, thread_sensitive=True)(pk=self.player.pk)

                # Send message to WebSocket
                await self.send(text_data=json.dumps({
                    'message': 'Вы заблокированы модератором ' + nickname,
                    'time': datetime.now().time().strftime("%H:%M"),
                    'id': self.player.pk,
                    'image': self.player.image.url,
                }))
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'id': self.player.pk,
                        'image': self.player.image.url,
                        'nickname': self.player.nickname,
                        'message': 'Пользователь заблокирован модератором ' + nickname,
                    }
                )

                self.disconnect()

        else:
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
                'time': datetime.now().time().strftime("%H:%M"),
                'id': id,
                'image': image,
                'nickname': nickname,
            }))
