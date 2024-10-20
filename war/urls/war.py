# coding=utf-8
from django.conf.urls import url
from django.urls import path

from war.views.character_wars import character_wars
from war.views.join_revolution import join_revolution
from war.views.open_war import open_war
from war.views.open_war_side_list import open_war_side_list
from war.views.start_war import start_war
from war.views.war_page import war_page
from war.views.switch_war_visibility import switch_war_visibility

urlpatterns = [

    # страница войн
    url(r'^wars$', war_page, name='war_page'),
    # начать ивентовую войну в регионе
    url(r'^start_war/$', start_war, name='start_war'),
    # открыть войну
    url(r'^war/(?P<class_name>[A-Za-z]+)/(?P<pk>\d+)/$', open_war, name='open_war'),

    # список воюющих за сторону
    path('war/<str:class_name>/<str:pk>/<str:side>/', open_war_side_list, name='open_war_side_list'),
    
    # урон игрока
    url(r'^character_wars/(?P<pk>\d+)/$', character_wars, name='character_wars'),

    # начать ивентовую войну в регионе
    url(r'^join_revolution/$', join_revolution, name='join_revolution'),

    # скрыть войну из списка боёв
    url(r'^switch_war_visibility/$', switch_war_visibility, name='switch_war_visibility'),
]
