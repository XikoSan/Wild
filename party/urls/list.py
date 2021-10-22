# coding=utf-8
from django.conf.urls import include, url

from party.views.lists.world_parties import world_parties_list
from party.views.lists.region_parties import region_parties_list
from party.views.lists.party_history import party_history_list

urlpatterns = [
    # открытие списка всех партий
    url(r'^world/parties/$', world_parties_list, name='world_parties_list'),
    # партии региона
    url(r'^region/(?P<region_pk>\d+)/parties/$', region_parties_list, name='world_parties_list'),

    # история партий игрока
    url(r'^party_history/(?P<char_pk>\d+)/$', party_history_list, name='party_history_list'),
]
