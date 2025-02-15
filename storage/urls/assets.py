# coding=utf-8
from django.conf.urls import include, url

from storage.views.assets.assets import assets
from storage.views.assets.assets_destroy import assets_destroy
from storage.views.assets.assets_info import assets_info
from storage.views.assets.assets_transfer import assets_transfer
from storage.views.assets.storage_move import storage_move

urlpatterns = [

    # страница активов
    url(r'^assets$', assets, name='assets'),
    # перемещение товаров между складами
    url(r'^assets_transfer/$', assets_transfer, name='assets_transfer'),
    # уничтожение товаров
    url(r'^assets_destroy/$', assets_destroy, name='assets_destroy'),

    url(r'^storage_move/$', storage_move, name='storage_move'),

    # запасы на складе (подзагрузка в Активах):
    url(r'^info/assets/(?P<pk>\d+)$', assets_info, name='assets_info'),

]
