import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

from player.player import Player


def _get_player(account):
    return Player.objects.get(account=account)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.player = await sync_to_async(Player.objects.get, thread_sensitive=True)(account=self.scope["user"])
        # self.player = sync_to_async(_get_player(account=self.scope["user"]), thread_sensitive=True)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

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

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': self.player.pk,
                'nickname': self.player.nickname,
                'image': self.player.image.url,
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        id = event['id']
        nickname = event['nickname']
        image = event['image']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'time': datetime.now().time().strftime("%H:%M"),
            'id': id,
            'nickname': nickname,
            'image': image,
        }))
