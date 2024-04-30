# coding=utf-8
from django.conf.urls import url
from skill.views.skills_list import skills_list
from skill.views.skill_cancel import skill_cancel

urlpatterns = [
    # Открытие страницы навыков
    url(r'^skills/$', skills_list, name='skills_list'),

    # отменить изучение навыка
    url(r'^skill_cancel/$', skill_cancel, name='skill_cancel'),

]
