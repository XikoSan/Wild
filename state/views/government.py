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
    player = Player.get_instance(account=request.user)

    state = parliament = has_voting = capital = next_voting_date = is_deputate = None

    # если в этом регионе есть государство
    if player.region.state:
        state = player.region.state

        # находим столицу
        capital = Capital.objects.get(state=state).region

        # если у государства есть парламент
        if Parliament.objects.filter(state=state).exists():

            parliament = Parliament.objects.get(state=state)
            # проверяем, депутат ли этого парла игрок или нет
            is_deputate = DeputyMandate.objects.filter(player=player, parliament=parliament).exists()

            # если в парламенте идут выборы
            if ParliamentVoting.objects.filter(running=True, parliament=parliament).exists():
                has_voting = True
            else:
                if ParliamentVoting.objects.filter(running=False, parliament=parliament, task__isnull=False).exists():
                    next_voting_date = \
                        ParliamentVoting.objects.get(running=False, parliament=parliament,
                                                     task__isnull=False).voting_start + timedelta(days=7)
                else:
                    next_voting_date = state.foundation_date + timedelta(days=7)

    # отправляем в форму
    return render(request, 'state/gov/government.html', {
        # самого игрока
        'player': player,
        # государство, в котором сейчас находится игрок
        'state': state,

        # столица государства
        'capital': capital,

        # парламент
        'parliament': parliament,
        # депутат
        'is_deputate': is_deputate,

        # идут выборы
        'has_voting': has_voting,
        # дата выборов
        'next_voting_date': next_voting_date,
    })
