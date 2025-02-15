# coding=utf-8
from django.conf.urls import url

from party.primaries.views.start_primaries import start_primaries
from party.primaries.views.vote_primaries import vote_primaries
from party.views.management.change_party_pic import change_party_pic
from party.views.management.color_change import party_color_change
from party.views.management.gold.give_party_gold import give_party_gold
from party.views.management.management import management
from party.views.management.new_party import new_party
from party.views.management.party_requests import party_requests
from party.views.management.rename_party import rename_party
from party.views.management.switch_description import switch_description
from party.views.management.switch_party_type import switch_party_type
from party.views.open_party import open_party
from party.views.party import party

urlpatterns = [

    # страница партии
    url(r'^party$', party, name='party'),
    # открытие страницы создания новой партии
    url(r'^new_party$', new_party, name='new_party'),
    # открыть страницу партии
    url(r'^party/(?P<pk>\d+)/$', open_party, name='open_party'),

    # управление партией
    url(r'^party_management$', management, name='party_management'),
    # переименование партии:
    url(r'^rename_party/$', rename_party, name='rename_party'),
    # сменить картинки партии:
    url(r'^change_party_pic/$', change_party_pic, name='change_party_pic'),
    # изменить описание партии:
    url(r'^switch_description/$', switch_description, name='switch_description'),
    # изменить тип партии
    url(r'^switch_party_type/$', switch_party_type, name='switch_party_type'),
    # изменить цвет партии
    url(r'^party_color_change/$', party_color_change, name='party_color_change'),
    # лист заявок в партию
    url(r'^party/requests/$', party_requests, name='party_requests'),

    # выдать золото партии
    url(r'^give_party_gold/$', give_party_gold, name='give_party_gold'),

    # праймериз
    url(r'^primaries/(?P<party_pk>\d+)/$', start_primaries, name='start_primaries'),
    # голосование на праймериз
    url(r'^primaries/vote/$', vote_primaries, name='vote_primaries'),

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
