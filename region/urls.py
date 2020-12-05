# coding=utf-8
from django.conf.urls import include, url

from .views.mining import mining
from .views.do_mining import do_mining

urlpatterns = [

    # страница добычи ресурсов
    url(r'^mining$', mining, name='mining'),
    # добыча ресурсов
    url(r'^do_mining$', do_mining, name='do_mining'),

]
