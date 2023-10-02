from django.conf.urls import url

from chat.views.buy_sticker_pack import buy_sticker_pack
from chat.views.stickers_shop import stickers_shop
from chat.views.stickers_shop import stickers_shop
from chat.views.messages.messages import messages
from chat.views.messages.dialogue import dialogue

urlpatterns = [
    # открытие страницы кошелька
    url(r'^stickers_shop/$', stickers_shop, name='stickers_shop'),
    # купить набор стикеров
    url(r'^buy_sticker_pack/$', buy_sticker_pack, name='buy_sticker_pack'),

    # диалоги
    url(r'^im/$', messages, name='messages'),
    # диалог с пользователем
    url(r'^im/(?P<pk>\d+)/$', dialogue, name='dialogue'),
]
