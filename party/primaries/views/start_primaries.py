from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from player.decorators.player import check_player

from player.player import Player
from party.party import Party

from party.primaries.primaries import Primaries
from party.primaries.primaries_bulletin import PrimBulletin


# открытие страницы праймериз
@login_required(login_url='/')
@check_player
def start_primaries(request, party_pk):
    # получаем персонажа
    player = Player.objects.get(account=request.user)
    # если игрок состоит в партии, страницу которой хочет открыть, а также существуют АКТИВНЫЕ праймериз
    if player.party == Party.objects.get(pk=party_pk) \
            and Primaries.objects.filter(party=Party.objects.get(pk=party_pk), running=True).exists():
        vote = None
        # если игрок уже голосовал
        if PrimBulletin.objects.filter(primaries=Primaries.objects.get(party=Party.objects.get(pk=party_pk), running=True),player=player).exists():
            vote = PrimBulletin.objects.get(primaries=Primaries.objects.get(party=Party.objects.get(pk=party_pk), running=True),player=player)
        # отправляем в форму
        return render(request, 'primaries/primaries.html',
                      {'player': player,
                       'players_list': Player.objects.filter(party=Party.objects.get(pk=party_pk)),
                       'vote': vote})
    else:
        return redirect('party')