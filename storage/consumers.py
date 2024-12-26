import bleach
import json
import logging
import math
import pytz
import random
import re
import redis
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from datetime import timedelta
from django.apps import apps
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils import timezone
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _

from chat.models.messages.chat import Chat
from chat.models.messages.chat_members import ChatMembers
from chat.models.messages.message_block import MessageBlock
from chat.models.sticker import Sticker
from chat.models.stickers_ownership import StickersOwnership
from player.player import Player
from player.player_settings import PlayerSettings
from region.models.terrain.terrain_modifier import TerrainModifier
from skill.models.coherence import Coherence
from skill.models.scouting import Scouting
from storage.models.stock import Stock
from storage.models.storage import Storage
from war.models.wars.unit import Unit
from player.logs.print_log import log

def _get_player(account):
    return Player.objects.select_related('account').get(account=account)


class LootboxConsumer(AsyncWebsocketConsumer):

    async def connect(self):


        log('кря2')

        self.room_name = "lootboxes_channel"
        self.room_group_name = "lootboxes_channel"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):
        # Удаляем из группы
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Обработка сообщения от клиента
        data = json.loads(text_data)
        action = data.get("action")

        if action == "purchase":
            # Покупка лутбоксов
            lootbox_count = int(data.get("count", 0))
            total_value = lootbox_count * 100000

            # Отправляем другим клиентам
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "broadcast_purchase",
                    "player": self.player["name"],
                    "value": total_value,
                }
            )

    async def broadcast_purchase(self, event):
        # Отправка данных всем подключённым клиентам
        await self.send(text_data=json.dumps({
            "type": "purchase",
            "value": event["value"],
        }))

    async def broadcast_win(self, event):
        # Отправка выигрыша всем подключённым клиентам
        await self.send(text_data=json.dumps({
            "type": "win",
            "reward": event["reward"],
        }))
