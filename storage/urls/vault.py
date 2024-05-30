# coding=utf-8
from django.conf.urls import include, url

from storage.views.vault.produce_energy import produce_energy
from storage.views.vault.use_card import use_card
from storage.views.vault.lootbox import lootbox
from storage.views.vault.avia_box.avia_lootbox import avia_lootbox
from storage.views.vault.avia_box.open_aviaboxes import open_aviaboxes
from storage.views.vault.avia_box.loot_aviaboxes import loot_aviaboxes

urlpatterns = [

    # производство энергии:
    url(r'^produce_energy/$', produce_energy, name='produce_energy'),
    # активация премиум-карты:
    url(r'^use_card/$', use_card, name='use_card'),

    # страница лутбоксов
    url(r'^lootbox$', avia_lootbox, name='lootbox'),

    # открыть авиа-боксы
    url(r'^open_aviaboxes/$', open_aviaboxes, name='open_aviaboxes'),
    # забрать авиа-боксы
    url(r'^loot_aviaboxes/$', loot_aviaboxes, name='loot_aviaboxes'),

]
