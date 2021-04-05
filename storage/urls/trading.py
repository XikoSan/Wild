# coding=utf-8
from django.conf.urls import include, url

from storage.views.trading.create_offer import create_offer
from storage.views.trading.get_offers import get_offers
from storage.views.trading.new_offer import new_offer
from storage.views.trading.trading import trading

urlpatterns = [

    url(r'^trading$', trading, name='trading'),
    url(r'^new_offer$', new_offer, name='new_offer'),
    url(r'^create_offer/$', create_offer, name='create_offer'),
    url(r'^get_offers/$', get_offers, name='get_offers'),

]
