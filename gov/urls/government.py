# coding=utf-8
from django.conf.urls import url

from gov.views.color_change import state_color_change
from gov.views.custom_rights.foreign.residency_accept import residency_accept
from gov.views.custom_rights.foreign.residency_reject import residency_reject
from gov.views.custom_rights.foreign.residency_reject_all import residency_reject_all
from gov.views.manage_view import manage_view
from gov.views.ministers_manage import ministers_manage
from gov.views.open_pres_elections import open_pres_elections
from gov.views.set_ministers import set_ministers
from gov.views.switch_description import switch_description
from gov.views.vote_pres_elections import vote_pres_elections

urlpatterns = [
    # открытие страницы праймериз
    url(r'^presidential/(?P<pres_pk>\d+)/$', open_pres_elections, name='pres_elections'),
    # голосование на выборах
    url(r'^presidential/vote/(?P<pres_pk>\d+)/(?P<cand_pk>\d+)/$', vote_pres_elections, name='vote_pres_elections'),

    # управление государством
    url(r'^state_manage/$', manage_view, name='state_manage'),
    # изменить описание госа:
    url(r'^switch_state_description/$', switch_description, name='switch_state_description'),
    # изменить цвет госа
    url(r'^state_color_change/$', state_color_change, name='state_color_change'),

    # управление министрами
    url(r'^ministers_manage/$', ministers_manage, name='ministers_manage'),
    # назначить министров
    url(r'^set_ministers/$', set_ministers, name='set_ministers'),

    # права МИД: отклонить все заявки на прописку
    url(r'^residency_reject_all/$', residency_reject_all, name='residency_reject_all'),
    # права МИД: отклонить заявку на прописку
    url(r'^residency_reject/$', residency_reject, name='residency_reject'),
    # права МИД: одобрить заявку на прописку
    url(r'^residency_accept/$', residency_accept, name='residency_accept'),
]
