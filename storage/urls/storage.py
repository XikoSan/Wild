# coding=utf-8
from django.conf.urls import include, url

from storage.views.cash_transfer import cash_transfer
from storage.views.get_storage_action_line import get_storage_action_line
from storage.views.new_storage import new_storage
from storage.views.storage import storage
from storage.views.storage_status import storage_status

urlpatterns = [

    # страница склада
    url(r'^storage$', storage, name='storage'),
    # новый склад
    url(r'^new_storage/$', new_storage, name='new_storage'),

    # передача денег:
    url(r'^cash_transfer/$', cash_transfer, name='cash_transfer'),

    # строчка действий на Складе
    url(r'^storage/(?P<type>[\w\-]+)/$', get_storage_action_line, name='get_storage_action_line'),
    # статус склада
    url(r'^status/(?P<pk>.*)/$', storage_status, name='storage_status'),
]
