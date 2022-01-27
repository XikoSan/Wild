# coding=utf-8
from django.conf.urls import url

from polls.views.open_poll import open_poll
from polls.views.vote_poll import vote_poll

urlpatterns = [
    # открыть страницу опроса
    url(r'^poll/(?P<pk>\d+)/$', open_poll, name='open_poll'),
    # голосование в опросе
    url(r'^poll/vote/(?P<poll_pk>\d+)/(?P<variant_pk>\d+)/$', vote_poll, name='vote_poll'),
]
