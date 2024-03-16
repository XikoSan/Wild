# chat/routing.py
from django.urls import re_path

from . import consumers
from . import dialogue_consumers
from . import comment_consumers

websocket_urlpatterns = [
    re_path(r'wss/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),

    re_path(r'wss/comments/(?P<room_name>\w+)/$', comment_consumers.ChatConsumer.as_asgi()),

    re_path(r'wss/dialogue/(?P<room_name>\w+)/$', dialogue_consumers.ChatConsumer.as_asgi()),
]
