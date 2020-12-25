# coding=utf-8
from django.conf.urls import include, url

# from party.views.management.staff.request_in_party import request_in_party
from party.views.management.staff.join_in_party import join_in_party
from party.views.management.staff.leave_party import leave_party
from .views.party import party

urlpatterns = [

    # страница партии
    url(r'^party$', party, name='party'),
    # открытие буферной страницы вступления в партию,
    # где проверяется его принадлежность к аккаунту и перекидывает
    # на страницу партии, но уже как игрока одной из партий
    url(r'^join/(?P<plr_pk>\d+)/(?P<pty_pk>\d+)/$', join_in_party, name='party_joiner'),
    # покинуть партию
    url(r'^leave/(?P<party_id>\d+)/$', leave_party, name='party_leaver')
    # открытие буферной страницы подачи заявки в партию

]
