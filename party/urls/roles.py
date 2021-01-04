# coding=utf-8
from django.conf.urls import include, url

from party.views.management.roles.set_role import set_role

urlpatterns = [

    # назначить роль игроку партии:
    url(r'^set_role/$', set_role, name='set_role'),
]
