from django.conf.urls import url

from chat.views.buy_sticker_pack import buy_sticker_pack
from chat.views.messages.dialogue import dialogue
from chat.views.messages.dialogues import dialogues
from chat.views.messages.get_message_block import get_message_block
from chat.views.messages.mass_sending.create_admin_sending import create_admin_sending
from chat.views.messages.mass_sending.new_admin_sending import new_admin_sending
from chat.views.stickers_shop import stickers_shop

urlpatterns = [
    # открытие страницы кошелька
    url(r'^stickers_shop/$', stickers_shop, name='stickers_shop'),
    # купить набор стикеров
    url(r'^buy_sticker_pack/$', buy_sticker_pack, name='buy_sticker_pack'),

    # диалоги
    url(r'^im/$', dialogues, name='dialogues'),
    # диалог с пользователем
    url(r'^im/(?P<pk>\d+)/$', dialogue, name='dialogue'),
    # получить блок сообщений
    url(r'^load_message_block$', get_message_block, name='get_message_block'),

    # страница новой рассылки
    url(r'^new_admin_sending/$', new_admin_sending, name='new_admin_sending'),
    # новая рассылка админа
    url(r'^create_admin_sending/$', create_admin_sending, name='create_admin_sending'),
]
