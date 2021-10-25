# coding=utf-8
from django.conf.urls import url

from war.views.open_war import open_war
from war.views.start_war import start_war
from war.views.war_page import war_page
from war.views.send_squads import send_squads

urlpatterns = [

    # страница войн
    url(r'^wars$', war_page, name='war_page'),
    # начать ивентовую войну в регионе
    url(r'^start_war/$', start_war, name='start_war'),
    # открыть войну
    url(r'^war/(?P<class_name>[A-Za-z]+)/(?P<pk>\d+)/$', open_war, name='open_war'),

    # отправить войска в отряды
    url(r'^send_squads/$', send_squads, name='send_squads'),
]
