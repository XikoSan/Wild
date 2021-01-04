# coding=utf-8
from django.conf.urls import include, url

from party.views.management.roles.new_role import new_role
from party.views.management.roles.remove_role import remove_role
from party.views.management.roles.set_role import set_role

urlpatterns = [

    # назначить роль игроку партии:
    url(r'^set_role/$', set_role, name='set_role'),
    # добавить роль в партии:
    url(r'^new_role/$', new_role, name='new_role'),
    # удалить роль в партии:
    url(r'^remove_role/$', remove_role, name='remove_role'),
]
