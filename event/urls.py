# coding=utf-8
from django.conf.urls import url
from event.views.inviting_event import inviting_event
from event.views.activate_invite import activate_invite
from event.views.invited_list import invited_list

urlpatterns = [
    # открыть страницу ивента
    url(r'^inviting_event/$', inviting_event, name='inviting_event'),

    # активация бонус-кода
    url(r'^activate_invite/', activate_invite, name='activate_invite'),

    # Приглашенные игроком
    url(r'^invited/(?P<pk>\d+)/$', invited_list, name='invited_list'),
]
