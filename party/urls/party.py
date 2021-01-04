# coding=utf-8
from django.conf.urls import include, url

from party.views.management.new_party import new_party
from party.views.management.party_requests import party_requests
from party.views.party import party

urlpatterns = [

    # страница партии
    url(r'^party$', party, name='party'),
    # открытие страницы создания новой партии
    url(r'^new_party$', new_party, name='new_party'),

    # лист заявок в партию
    url(r'^party/requests/$', party_requests, name='party_requests'),

]
# # -------------- Партия --------------------
#
#
#     # управление партией
#     url(r'^party_management$', party_management.PartyManagement, name='party_management'),
#     # переименование партии:
#     url(r'^rename_party/$', rename_party.RenameParty, name='rename_party'),
#     # изменить описание партии:
#     url(r'^deskr_party/$', deskr_party.DeskrParty, name='deskr_party'),
#     # изменить клановый герб:
#     url(r'^change_party_coat/$', party_coat.CoatParty, name='coat_party'),
#     # изменить клановый фон:
#     url(r'^change_party_back/$', background.BackgroundParty, name='back_party'),
#     # изменить тип партии
#     url(r'^party_type_change/(?P<party_pk>\d+)/$', party_type_change.PartyTypeChange, name='party_type_changer'),
#     # добавить роль в партии:
#     url(r'^new_role_at_party/$', new_role.NewRole, name='new_role'),
#     # удалить роль в партии:
#     url(r'^rm_role_at_party/$', remove_role.RmRole, name='rm_role'),


#     # открытие буферной страницы принятия в партию,
#     # где проверяются права принимающего в партию
#     # на страницу партии, но уже как игрока одной из партий
#     url(r'^char/(?P<plr_pk>\d+)/accept/(?P<pty_pk>\d+)/$', accept_in_party.AcceptInParty, name='party_accepter'),
#     # отклонение заявки в партию
#     url(r'^char/(?P<plr_pk>\d+)/decline/(?P<pty_pk>\d+)/$', decline_party_request.DeclinePartyRequest,
#         name='party_decliner'),
#     # отклонение всех заявок в партию
#     url(r'^dismiss/party/(?P<pty_pk>\d+)/$', dismiss_all_requests.DismissAllRequests, name='party_dismiss_all'),
#     # лист заявок в партию
#     url(r'^party/(?P<party_pk>\d+)/requests/$', party_requests.PartyRequests, name='party_requests'),
#     # открытие страницы праймериз
#     url(r'^primaries/(?P<party_pk>\d+)/$', open_primaries.OpenPrimaries, name='party_primaries'),
#     # голосование на праймериз
#     url(r'^primaries/vote/(?P<party_pk>\d+)/(?P<player_pk>\d+)/$',
#         vote_primaries.VotePrimaries, name='vote_primaries'),
