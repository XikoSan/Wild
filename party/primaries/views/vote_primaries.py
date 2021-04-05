from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from player.decorators.player import check_player

from party.party import Party
from player.player import Player

from party.primaries.primaries import Primaries
from party.primaries.primaries_bulletin import PrimBulletin

# проголосовать на праймериз
@login_required(login_url='/')
@check_player
def vote_primaries(request, party_pk, player_pk):
    # получаем персонажа
    player = Player.objects.get(account=request.user)
    # если игрок состоит в партии, на праймериз которой голосует,
    # если игрок ещё НЕ голосовал вообще
    #  а также существуют АКТИВНЫЕ праймериз,
    #  а кандидат состоит в этой партии (вдруг вышел пока открывали страницу)
    if player.party == Party.objects.get(pk=party_pk)\
            and not PrimBulletin.objects.filter(primaries=Primaries.objects.get(party=Party.objects.get(pk=party_pk), running=True), player=player).exists()\
            and Primaries.objects.filter(party=Party.objects.get(pk=party_pk), running=True).exists()\
            and Player.objects.filter(pk=player_pk, party=party_pk).exists():
        # создаем новый бюллетень голосования за переданного игрока
        vote = PrimBulletin(primaries=Primaries.objects.get(party=Party.objects.get(pk=party_pk), running=True),
                            player=player,
                            candidate=Player.objects.get(pk=player_pk))
        # сохраняем бюллетень
        vote.save()

    return redirect('party')