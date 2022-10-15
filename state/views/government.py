from datetime import timedelta
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from gov.models.custom_rights.custom_right import CustomRight
from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from state.models.capital import Capital
from player.views.get_subclasses import get_subclasses
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.parliament.parliament_party import ParliamentParty
from state.models.parliament.parliament_voting import ParliamentVoting
from state.models.treasury import Treasury
from gov.models.minister import Minister


# страница правительства государства
@login_required(login_url='/')
@check_player
def government(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    state = parliament = has_voting = capital = next_voting_date = is_deputate = has_custom_right = None

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

            if is_deputate and Minister.objects.filter(player=player, state=state).exists():

                minister = Minister.objects.get(player=player, state=state)
                custom_rights = CustomRight.__subclasses__()

                for c_right in custom_rights:
                    for min_rights in minister.rights.all():
                        if c_right.__name__ == min_rights.right:
                            has_custom_right = True

            # если в парламенте идут выборы
            if ParliamentVoting.objects.filter(running=True, parliament=parliament).exists():
                has_voting = True
            else:
                if ParliamentVoting.objects.filter(running=False, parliament=parliament).exists():
                    next_voting_date = \
                        ParliamentVoting.objects.get(running=False, parliament=parliament).voting_start + timedelta(days=7)
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
        # имеет особые права министра
        'has_custom_right': has_custom_right,

        # идут выборы
        'has_voting': has_voting,
        # дата выборов
        'next_voting_date': next_voting_date,
    })
