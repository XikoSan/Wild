# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # re_path(r'wss/war_chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'wss/lootboxes/$', consumers.LootboxConsumer.as_asgi()),
]
