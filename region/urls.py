# coding=utf-8
from django.conf.urls import url

from .views.do_mining import do_mining
from .views.map.map import map
from .views.map.open_region import open_region
from .views.map.region_info import region_info
from .views.mining import mining

urlpatterns = [

    # страница добычи ресурсов
    url(r'^mining$', mining, name='mining'),
    # добыча ресурсов
    url(r'^do_mining$', do_mining, name='do_mining'),

    # карта
    url(r'^map$', map, name='map'),
    # информация о регионе:
    url(r'^info/region/(?P<id>[A-Z]+-[A-Z]+)$', region_info, name='region_info'),

    # Opening page of the state
    url(r'^region/(?P<pk>\d+)/$', open_region, name='open_region'),

]
