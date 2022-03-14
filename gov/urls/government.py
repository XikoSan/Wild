# coding=utf-8
from django.conf.urls import url

from gov.views.open_pres_elections import open_pres_elections
from gov.views.vote_pres_elections import vote_pres_elections

urlpatterns = [
    # открытие страницы праймериз
    url(r'^presidential/(?P<pres_pk>\d+)/$', open_pres_elections, name='pres_elections'),
    # голосование на выборах
    url(r'^presidential/vote/(?P<pres_pk>\d+)/(?P<cand_pk>\d+)/$', vote_pres_elections, name='vote_pres_elections'),
]
