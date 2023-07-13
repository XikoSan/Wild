# coding=utf-8
from django.conf.urls import include, url

from storage.views.assets.assets import assets
from storage.views.assets.assets_action import assets_action
from storage.views.assets.storage_move import storage_move
from storage.views.assets.assets_transfer import assets_transfer
from storage.views.assets.assets_destroy import assets_destroy

urlpatterns = [

    # страница активов
    url(r'^assets$', assets, name='assets'),

    # новый склад
    # url(r'^assets_action/$', assets_action, name='assets_action'),

    # перемещение товаров между складами
    url(r'^assets_transfer/$', assets_transfer, name='assets_transfer'),
    # уничтожение товаров
    url(r'^assets_destroy/$', assets_destroy, name='assets_destroy'),

    url(r'^storage_move/$', storage_move, name='storage_move'),

]
