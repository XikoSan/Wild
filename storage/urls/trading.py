# coding=utf-8
from django.conf.urls import include, url

from storage.views.trading.trading import trading

urlpatterns = [

    url(r'^trading$', trading, name='trading'),

]
