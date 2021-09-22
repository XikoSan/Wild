# coding=utf-8
from django.conf.urls import include, url

from .views.index import index
from .views.overview import overview
from .views.new_player import new_player
from .views.expense_energy import expense_energy
from .views.my_profile import my_profile
from .views.view_profile import view_profile

urlpatterns = [

    # приветственная страница
    url(r'^$', index, name='index'),
    # регистрация нового персонажа
    url(r'^player/new/$', new_player, name='new_player'),
    # выход
    # url(r'^logout', logout.LogoutView.as_view(), name='logout'),

    # открытие "обзора"
    url(r'^overview$', overview, name='overview'),
    # пополнение энергии:
    url(r'^recharge/$', expense_energy, name='expense_energy'),

    # открытие страницы персонажа игрока
    url(r'^profile/$', my_profile, name='my_profile'),
    # Открытие профиля персонажа для просмотра(другими игроками)
    url(r'^profile/(?P<pk>\d+)/$', view_profile, name='view_profile'),
]
