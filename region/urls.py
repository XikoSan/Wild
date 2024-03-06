# coding=utf-8
from django.conf.urls import url

from region.views.cancel_auto import cancel_auto
from region.views.start_auto import start_auto
from .views.do_mining import do_mining
from .views.lists.world_regions import world_regions_list
from .views.map.get_residency import get_residency
from .views.map.map import map
from .views.map.open_region import open_region
from .views.map.region_info import region_info
from .views.mining import mining
from .views.retrieve_cash import retrieve_cash
from .views.daily_status import daily_status
from region.views.map.save_links import save_links

urlpatterns = [

    # страница добычи ресурсов
    url(r'^mining$', mining, name='mining'),
    # добыча ресурсов
    url(r'^do_mining$', do_mining, name='do_mining'),
    # получение денег из дейлика
    url(r'^retrieve_cash$', retrieve_cash, name='retrieve_cash'),
    # получение информации о дейлике
    url(r'^daily_status$', daily_status, name='daily_status'),

    # добыча ресурсов АВТО
    url(r'^start_auto/$', start_auto, name='start_auto'),
    # отмена добыча ресурсов АВТО
    url(r'^cancel_auto/$', cancel_auto, name='cancel_auto'),

    # карта
    url(r'^map$', map, name='map'),
    # информация о регионе:
    url(r'^info/region/(?P<id>[A-Z]+-[A-Z]+)$', region_info, name='region_info'),

    # открыть страницу региона
    url(r'^region/(?P<pk>\d+)/$', open_region, name='open_region'),
    # получить прописку в регине
    url(r'^get_residency/$', get_residency, name='get_residency'),

    # открытие списка всех игроков
    url(r'^world/regions/', world_regions_list, name='world_players_list'),

    # сохранить список связей регионов
    url(r'^save_links', save_links, name='save_links'),

]
