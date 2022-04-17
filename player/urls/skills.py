# coding=utf-8
from django.conf.urls import url

from player.views.skills.skill_queue import skill_queue
from player.views.skills.up_skill import up_skill

urlpatterns = [

    # изучить навык
    url(r'^up_skill/$', up_skill, name='up_skill'),

    # просмотр очереди навыков:
    url(r'^skill_queue/$', skill_queue, name='skill_queue'),
]
