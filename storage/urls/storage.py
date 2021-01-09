# coding=utf-8
from django.conf.urls import include, url

from storage.views.assets import assets
from storage.views.new_storage import new_storage
from storage.views.storage import storage

urlpatterns = [

    # страница склада
    url(r'^storage$', storage, name='storage'),
    # новый склад
    url(r'^new_storage/$', new_storage, name='new_storage'),

    # страница активов
    url(r'^assets$', assets, name='assets'),
]
