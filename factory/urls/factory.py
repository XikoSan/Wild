# coding=utf-8
from django.conf.urls import include, url

from factory.views.factory import factory
from factory.views.produce_good import produce_good

urlpatterns = [

    # страница производства
    url(r'^factory$', factory, name='factory'),
    # произвести товар
    url(r'^produce/$', produce_good, name='produce_good'),
]
