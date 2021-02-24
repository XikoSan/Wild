# coding=utf-8
from django.conf.urls import include, url

from storage.views.assets.assets import assets
from storage.views.assets.assets_action import assets_action

urlpatterns = [

    # страница активов
    url(r'^assets$', assets, name='assets'),

    # новый склад
    url(r'^assets_action/$', assets_action, name='assets_action'),

]
