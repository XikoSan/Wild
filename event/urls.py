# coding=utf-8
from django.conf.urls import url
from event.views.inviting_event import inviting_event
from event.views.activate_invite import activate_invite

urlpatterns = [
    # открыть страницу ивента
    url(r'^inviting_event/$', inviting_event, name='inviting_event'),

    # активация бонус-кода
    url(r'^activate_invite/', activate_invite, name='activate_invite'),
]
