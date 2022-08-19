# coding=utf-8
from django.conf.urls import url
from skill.views.skills_list import skills_list

urlpatterns = [
    # Открытие страницы навыков
    url(r'^skills/$', skills_list, name='skills_list'),
]
