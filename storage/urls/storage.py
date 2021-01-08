# coding=utf-8
from django.conf.urls import include, url

from storage.views.storage import storage
from storage.views.assets import assets

urlpatterns = [

    # страница склада
    url(r'^storage$', storage, name='storage'),

    # страница склада
    url(r'^assets$', assets, name='assets'),
]
