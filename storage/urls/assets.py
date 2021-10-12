# coding=utf-8
from django.conf.urls import include, url

from storage.views.assets.assets import assets
from storage.views.assets.assets_action import assets_action
from storage.views.assets.storage_move import storage_move

urlpatterns = [

    # страница активов
    url(r'^assets$', assets, name='assets'),

    # новый склад
    url(r'^assets_action/$', assets_action, name='assets_action'),

    url(r'^storage_move/$', storage_move, name='storage_move'),

]
