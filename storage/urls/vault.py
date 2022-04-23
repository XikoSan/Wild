# coding=utf-8
from django.conf.urls import include, url

from storage.views.vault.produce_energy import produce_energy
from storage.views.vault.use_card import use_card

urlpatterns = [

    # производство энергии:
    url(r'^produce_energy/$', produce_energy, name='produce_energy'),
    # активация премиум-карты:
    url(r'^use_card/$', use_card, name='use_card'),
]
