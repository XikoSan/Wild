# coding=utf-8
from django.conf.urls import url

from education.views.edu_election import edu_election
from education.views.edu_gov import edu_gov
from education.views.edu_map import edu_map
from education.views.edu_mining import edu_mining
from education.views.edu_overview import edu_overview
from education.views.edu_produce import edu_produce
from education.views.edu_reward import edu_reward
from education.views.edu_war import edu_war

urlpatterns = [

    # получение наград за обучение
    url(r'^edu_reward/$', edu_reward, name='edu_reward'),

    # учебная страница Обзора
    url(r'^edu_1$', edu_overview, name='edu_overview'),

    # учебная страница голосования
    url(r'^edu_2$', edu_election, name='edu_election'),

    # учебная страница парламента
    url(r'^edu_3$', edu_gov, name='edu_gov'),

    # учебная страница восстания
    url(r'^edu_4$', edu_war, name='edu_war'),

    # учебная страница карты
    url(r'^edu_5$', edu_map, name='edu_map'),

    # учебная страница добычи
    url(r'^edu_6$', edu_mining, name='edu_mining'),

    # учебная страница добычи
    url(r'^edu_7$', edu_produce, name='edu_produce'),

]
