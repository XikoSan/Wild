# coding=utf-8
from django.conf.urls import url
from django.urls import path

from war.views.character_wars import character_wars
from war.views.open_war import open_war
from war.views.open_war_side_list import open_war_side_list
from war.views.send_squads import send_squads
from war.views.start_war import start_war
from war.views.war_page import war_page

urlpatterns = [

    # страница войн
    url(r'^wars$', war_page, name='war_page'),
    # начать ивентовую войну в регионе
    url(r'^start_war/$', start_war, name='start_war'),
    # открыть войну
    url(r'^war/(?P<class_name>[A-Za-z]+)/(?P<pk>\d+)/$', open_war, name='open_war'),

    # отправить войска в отряды
    url(r'^send_squads/$', send_squads, name='send_squads'),

    # список воюющих за сторону
    path('war/<str:class_name>/<str:pk>/<str:side>/', open_war_side_list, name='open_war_side_list'),
    
    # урон игрока
    url(r'^character_wars/(?P<pk>\d+)/$', character_wars, name='character_wars'),
]
