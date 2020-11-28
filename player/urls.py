# coding=utf-8
from django.conf.urls import include, url

from .views.index import index
from .views.overview import overview
from .views.new_player import new_player

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
    # url(r'^recharge/$', expense_energy.ExpenseEnergy, name='expense_energy'),

]
