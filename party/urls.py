# coding=utf-8
from django.conf.urls import include, url

from party.views.management.new_party import new_party
from party.views.management.roles.set_role import set_role
from party.views.management.staff.cancel_request_in_party import cancel_request_in_party
from party.views.management.staff.join_in_party import join_in_party
from party.views.management.staff.kick_from_party import kick_from_party
from party.views.management.staff.leave_party import leave_party
from party.views.management.staff.request_in_party import request_in_party
from party.views.party import party

urlpatterns = [

    # страница партии
    url(r'^party$', party, name='party'),
    # открытие буферной страницы вступления в партию,
    # где проверяется его принадлежность к аккаунту и перекидывает
    # на страницу партии, но уже как игрока одной из партий
    url(r'^join/(?P<plr_pk>\d+)/(?P<pty_pk>\d+)/$', join_in_party, name='party_joiner'),
    # покинуть партию
    url(r'^leave/$', leave_party, name='party_leaver'),
    # открытие буферной страницы подачи заявки в партию
    url(r'^request/(?P<plr_pk>\d+)/(?P<pty_pk>\d+)/$', request_in_party,
        name='party_request'),
    # открытие буферной страницы отмены заявки в партию
    url(r'^cancel/(?P<plr_pk>\d+)/(?P<pty_pk>\d+)/$', cancel_request_in_party,
        name='party_cancel'),
    # назначить роль игроку партии:
    url(r'^set_role/$', set_role, name='set_role'),

    # открытие страницы создания новой партии
    url(r'^new_party$', new_party, name='new_party'),
    # исключить из партии
    url(r'^kick/(?P<pk>\d+)/$', kick_from_party, name='party_kick'),
]
