# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # re_path(r'wss/war_chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'wss/war/(?P<war_type>\w+)/(?P<war_id>\w+)/$', consumers.WarConsumer.as_asgi()),
]
