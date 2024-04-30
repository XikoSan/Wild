# coding=utf-8
from django.conf.urls import url

from player.views.skills.skill_queue import skill_queue
from player.views.skills.up_skill import up_skill
from player.views.skills.boost_skill import boost_skill

urlpatterns = [

    # изучить навык
    url(r'^up_skill/$', up_skill, name='up_skill'),

    # просмотр очереди навыков:
    url(r'^skill_queue/$', skill_queue, name='skill_queue'),

    # ускорить изучение навыка
    url(r'^boost_skill/$', boost_skill, name='boost_skill'),
]
