# coding=utf-8
from django.conf.urls import include, url

from storage.views.factory.factory import factory

urlpatterns = [

    # страница производства
    url(r'^factory$', factory, name='factory'),
]
