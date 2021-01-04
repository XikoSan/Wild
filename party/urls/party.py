# coding=utf-8
from django.conf.urls import include, url

from party.views.management.management import management
from party.views.management.new_party import new_party
from party.views.management.party_requests import party_requests
from party.views.management.rename_party import rename_party
from party.views.management.switch_description import switch_description
from party.views.management.switch_party_coat import switch_party_coat
from party.views.management.switch_party_type import switch_party_type
from party.views.party import party

urlpatterns = [

    # страница партии
    url(r'^party$', party, name='party'),
    # открытие страницы создания новой партии
    url(r'^new_party$', new_party, name='new_party'),

    # управление партией
    url(r'^party_management$', management, name='party_management'),
    # переименование партии:
    url(r'^rename_party/$', rename_party, name='rename_party'),
    # изменить описание партии:
    url(r'^switch_description/$', switch_description, name='switch_description'),
    # изменить тип партии
    url(r'^switch_party_type/$', switch_party_type, name='switch_party_type'),

    # лист заявок в партию
    url(r'^party/requests/$', party_requests, name='party_requests'),

]
# # -------------- Партия --------------------
#
#
#     # изменить  фон:
#     url(r'^change_party_back/$', background.BackgroundParty, name='back_party'),
# # изменить  герб:
# url(r'^switch_party_coat/$', switch_party_coat, name='switch_party_coat'),

#     # открытие страницы праймериз
#     url(r'^primaries/(?P<party_pk>\d+)/$', open_primaries.OpenPrimaries, name='party_primaries'),
#     # голосование на праймериз
#     url(r'^primaries/vote/(?P<party_pk>\d+)/(?P<player_pk>\d+)/$',
#         vote_primaries.VotePrimaries, name='vote_primaries'),
