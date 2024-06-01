# coding=utf-8
from django.conf.urls import url

from player.views.customization.border.border_select import border_select
from player.views.customization.border.choose_border import choose_border
from player.views.customization.plane.choose_plane import choose_plane
from player.views.customization.plane.clear_plane_nick import clear_plane_nick
from player.views.customization.plane.plane_select import plane_select
from player.views.customization.plane.set_plane_nick import set_plane_nick

urlpatterns = [

    # страница выбора самолетов
    url(r'^plane_select/$', plane_select, name='plane_select'),

    # выбор самолетов
    url(r'^choose_plane/$', choose_plane, name='choose_plane'),

    # установить позывной самолета
    url(r'^set_plane_nick/$', set_plane_nick, name='set_plane_nick'),

    # очистить позывной самолета
    url(r'^clear_plane_nick/$', clear_plane_nick, name='clear_plane_nick'),

    # страница выбора рамок
    url(r'^border_select/$', border_select, name='border_select'),

    # выбор самолетов
    url(r'^choose_border/$', choose_border, name='choose_border'),
]
