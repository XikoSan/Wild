# coding=utf-8
from django.conf.urls import include, url

from party.views.management.staff.accept_in_party import accept_in_party
from party.views.management.staff.cancel_request_in_party import cancel_request_in_party
from party.views.management.staff.decline_party_request import decline_party_request
from party.views.management.staff.dismiss_all_requests import dismiss_all_requests
from party.views.management.staff.join_in_party import join_in_party
from party.views.management.staff.kick_from_party import kick_from_party
from party.views.management.staff.leave_party import leave_party
from party.views.management.staff.request_in_party import request_in_party

# from party.views.management import staff

urlpatterns = [

    # открытие буферной страницы отмены заявки в партию
    url(r'^cancel/(?P<plr_pk>\d+)/(?P<pty_pk>\d+)/$', cancel_request_in_party,
        name='party_cancel'),
    # открытие буферной страницы вступления в партию,
    # где проверяется его принадлежность к аккаунту и перекидывает
    # на страницу партии, но уже как игрока одной из партий
    url(r'^join/(?P<plr_pk>\d+)/(?P<pty_pk>\d+)/$', join_in_party, name='party_joiner'),
    # исключить из партии
    url(r'^kick/(?P<pk>\d+)/$', kick_from_party, name='party_kick'),
    # покинуть партию
    url(r'^leave/$', leave_party, name='party_leaver'),
    # открытие буферной страницы подачи заявки в партию
    url(r'^request/(?P<plr_pk>\d+)/(?P<pty_pk>\d+)/$', request_in_party,
        name='party_request'),

    # отклонение всех заявок в партию
    url(r'^dismiss/party/$', dismiss_all_requests, name='party_dismiss_all'),
    # открытие буферной страницы принятия в партию,
    # где проверяются права принимающего в партию
    # на страницу партии, но уже как игрока одной из партий
    url(r'^char/(?P<plr_pk>\d+)/accept/$', accept_in_party, name='party_accepter'),
    # # отклонение заявки в партию
    url(r'^char/(?P<plr_pk>\d+)/decline/$', decline_party_request,
        name='party_decliner'),

]
