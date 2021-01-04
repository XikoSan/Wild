from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from itertools import chain

from party.party import Party
from party.party_apply import PartyApply
from party.primaries.primaries import Primaries
from party.primaries.primaries_leader import PrimariesLeader
from player.decorators.player import check_player
from player.player import Player


# Страница с запросами в партию
@login_required(login_url='/')
@check_player
def party_requests(request):
    # получаем персонажа
    player = Player.objects.get(account=request.user)
    # если у игрока есть должность в партии (то есть он состоит в ней)
    if player.party_post:
        # если игрок действительно лидер партии или хотя бы секретарь
        if player.party_post.party_lead or player.party_post.party_sec:
            # получаем партию
            party = Party.objects.get(pk=player.party.pk)
            # если партия открытая - никакого списка с заявками нет
            if party.type == 'op':
                return redirect('party')
            # создаем список кандидатов
            candidates = None
            # для каждого запроса в эту партию
            for pty_request in PartyApply.objects.filter(party=party, status='op'):
                # получаем экземпляр кандидата
                can_player = Player.objects.filter(pk=pty_request.player.pk)
                # если лист партий из парламента не пустой
                if candidates:
                    # добавляем партию к списку
                    candidates = list(chain(candidates, can_player))
                else:
                    candidates = can_player

            return render(request, 'party/party_requests.html',
                          {'player': player,
                           'players_list': candidates
                           })

        else:
            return redirect('party')
    else:
        return redirect('party')
