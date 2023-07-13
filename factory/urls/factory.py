# coding=utf-8
from django.conf.urls import include, url

from factory.views.factory import factory
from factory.views.produce_good import produce_good

from factory.views.cancel_auto import cancel_auto_produce
from factory.views.start_auto import start_auto_produce

urlpatterns = [

    # страница производства
    url(r'^factory$', factory, name='factory'),
    # произвести товар
    url(r'^produce/$', produce_good, name='produce_good'),

    # производство АВТО
    url(r'^start_auto_produce/$', start_auto_produce, name='auto_produce'),
    # отмена производства АВТО
    url(r'^cancel_auto_produce/$', cancel_auto_produce, name='cancel_auto_produce'),
]
