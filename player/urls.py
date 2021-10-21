# coding=utf-8
from django.conf.urls import url

from player.views.banned import banned
from player.views.lists.region_players import region_players_list
from player.views.lists.world_players import world_players_list
from .views.change_bio import change_bio
from .views.expense_energy import expense_energy
from .views.index import index
from .views.my_profile import my_profile
from .views.new_player import new_player
from .views.overview import overview
from .views.view_profile import view_profile

urlpatterns = [

    # приветственная страница
    url(r'^$', index, name='index'),
    # регистрация нового персонажа
    url(r'^player/new/$', new_player, name='new_player'),
    # выход
    # url(r'^logout', logout.LogoutView.as_view(), name='logout'),

    # открытие списка всех игроков
    url(r'^world/players/', world_players_list, name='world_players_list'),
    # открытие списка населения региона
    url(r'^region/(?P<region_pk>\d+)/players/', region_players_list, name='region_players_list'),

    # открытие "обзора"
    url(r'^overview$', overview, name='overview'),
    # пополнение энергии:
    url(r'^recharge/$', expense_energy, name='expense_energy'),

    # открытие страницы персонажа игрока
    url(r'^profile/$', my_profile, name='my_profile'),
    # изменить биографию
    url(r'^change_bio/$', change_bio, name='change_bio'),
    # Открытие профиля персонажа для просмотра(другими игроками)
    url(r'^profile/(?P<pk>\d+)/$', view_profile, name='view_profile'),

    # Открытие страницы забаненного игрока
    url(r'^banned/$', banned, name='banned'),
]
