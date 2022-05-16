# coding=utf-8
from django.conf.urls import url

from gov.views.ministers_manage import ministers_manage
from gov.views.open_pres_elections import open_pres_elections
from gov.views.set_ministers import set_ministers
from gov.views.vote_pres_elections import vote_pres_elections

urlpatterns = [
    # открытие страницы праймериз
    url(r'^presidential/(?P<pres_pk>\d+)/$', open_pres_elections, name='pres_elections'),
    # голосование на выборах
    url(r'^presidential/vote/(?P<pres_pk>\d+)/(?P<cand_pk>\d+)/$', vote_pres_elections, name='vote_pres_elections'),
    # управление министрами
    url(r'^ministers_manage/$', ministers_manage, name='ministers_manage'),
    # назначить министров
    url(r'^set_ministers/$', set_ministers, name='set_ministers'),
]
