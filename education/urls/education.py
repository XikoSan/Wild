# coding=utf-8
from django.conf.urls import url

from education.views.edu_election import edu_election
from education.views.edu_gov import edu_gov
from education.views.edu_overview import edu_overview

urlpatterns = [

    # учебная страница Обзора
    url(r'^edu_1$', edu_overview, name='edu_overview'),

    # учебная страница голосования
    url(r'^edu_2$', edu_election, name='edu_election'),

    # учебная страница голосования
    url(r'^edu_3$', edu_gov, name='edu_gov'),

]
