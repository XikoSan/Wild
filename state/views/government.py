from datetime import timedelta
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from state.models.capital import Capital
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.parliament.parliament_party import ParliamentParty
from state.models.parliament.parliament_voting import ParliamentVoting
from state.models.treasury import Treasury


# страница правительства государства
@login_required(login_url='/')
@check_player
def government(request):
    # получаем персонажа
    player = Player.objects.get(account=request.user)

    state = capital = has_parliament = None

    # если в этом регионе есть государство
    if player.region.state:
        state = player.region.state

        # находим столицу
        capital = Capital.objects.get(state=state).region

        # если у государства есть парламент
        if Parliament.objects.filter(state=state).exists():

            has_parliament = True

        # # если у государства есть парламент
        # if Parliament.objects.filter(state=state).exists():
        #     parliament = Parliament.objects.get(state=state)
        #     # если в парламенте идут выборы
        #     if ParliamentVoting.objects.filter(running=True, parliament=parliament).exists():
        #         parliament_voting = ParliamentVoting.objects.get(running=True, parliament=parliament)
        #     else:
        #         if ParliamentVoting.objects.filter(running=False, parliament=parliament, task__isnull=False).exists():
        #             next_voting_date = \
        #                 ParliamentVoting.objects.get(running=False, parliament=parliament,
        #                                              task__isnull=False).voting_start + timedelta(days=7)
        #         else:
        #             next_voting_date = state.foundation_date + timedelta(days=7)
        #     # если есть парламентские партии
        #     if ParliamentParty.objects.filter(parliament=parliament).exists():
        #         # для каждой парламентской партии
        #         for parl_party in ParliamentParty.objects.filter(parliament=parliament):
        #             # получаем экземпляр партии из объекта парламентской партии
        #             adding_party = Party.objects.get(pk=parl_party.party.pk)
        #             # для каждого игрока этой партии с мандатом
        #             for deputate in DeputyMandate.objects.filter(parliament=parliament, party=adding_party):
        #                 # получаем экземпляр депутата
        #                 dep_player = Player.objects.filter(pk=deputate.player.pk)
        #                 # если лист партий из парламента не пустой
        #                 if deputates:
        #                     # добавляем партию к списку
        #                     deputates = list(chain(deputates, dep_player))
        #                 else:
        #                     deputates = dep_player

    # отправляем в форму
    return render(request, 'state/gov/government.html', {
        # самого игрока
        'player': player,
        # государство, в котором сейчас находится игрок
        'state': state,

        # столица государства
        'capital': capital,

        # наличие парламента
        'has_parliament': has_parliament,
    })
