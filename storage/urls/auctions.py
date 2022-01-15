# coding=utf-8
from django.conf.urls import url

from storage.views.auctions.auction_info import auction_info
from storage.views.auctions.auctions import auctions
from storage.views.auctions.get_auctions import get_auctions
from storage.views.auctions.set_bet import set_bet

urlpatterns = [

    url(r'^auctions$', auctions, name='auctions'),
    # информация об аукционе:
    url(r'^auction/(?P<pk>\d+)/$', auction_info, name='auction_info'),
    # получить список аукционов
    url(r'^get_auctions/$', get_auctions, name='get_auctions'),
    # сделать ставку
    url(r'^set_bet/$', set_bet, name='set_bet'),

]
