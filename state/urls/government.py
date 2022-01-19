# coding=utf-8
from django.conf.urls import url

from state.views.government import government
from state.views.open_elections import open_elections
from state.views.set_mandate_view import set_mandate_view
from state.views.set_mandate import set_mandate
from state.views.state_foundation import state_foundation
from state.views.vote_elections import vote_elections
from state.views.open_state import open_state

urlpatterns = [

    # страница государства
    url(r'^government$', government, name='government'),
    # основание государства:
    url(r'^state_foundation/$', state_foundation, name='state_foundation'),
    # открыть страницу государства
    url(r'^state/(?P<pk>\d+)/$', open_state, name='open_state'),

    # открытие страницы праймериз
    url(r'^elections/(?P<parl_pk>\d+)/$', open_elections, name='parl_elections'),
    # голосование на выборах
    url(r'^elections/vote/(?P<parl_pk>\d+)/(?P<party_pk>\d+)/$', vote_elections, name='vote_elections'),

    # страница выдачи свободного манданта однопартийцу (только для главы партии)
    url(r'^set_mandate_view/$', set_mandate_view, name='set_mandate_view'),
    # выдать свободный мандант однопартийцу (только для главы партии)
    url(r'^set_mandate/$', set_mandate, name='set_mandate'),
]
