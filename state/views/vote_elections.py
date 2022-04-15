from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone

from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from region.region import Region
from state.models.parliament.bulletin import Bulletin
from state.models.parliament.parliament import Parliament
from state.models.parliament.parliament_voting import ParliamentVoting


# проголосовать на выборах в парламент государства
@login_required(login_url='/')
@check_player
def vote_elections(request, parl_pk, party_pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)
    # регионы государства, в котором идут выборы
    state = Parliament.objects.get(pk=parl_pk).state
    regions_of_state = Region.objects.filter(state=state)
    # право голосовать на текущих выборах.
    # Появляется, если с момента взятия прописки прошли сутки
    votingRight = False
    regions_of_state = Region.objects.filter(state=state)
    if regions_of_state.filter(pk=player.residency.pk).exists() \
            and player.residency_date + timedelta(days=1) < timezone.now():
        votingRight = True
    # если у игрока есть прописка в государстве,
    #  а также существуют АКТИВНЫЕ выборы,
    #  у него есть право на них голосовать
    #  и он на этих выборах ещё не голосовал
    #  партия ещё существует
    #  находится в этом же государстве (вдруг регион передадут)
    # и была основана ДО начала выборов
    if regions_of_state.filter(pk=player.residency.pk).exists() \
            and ParliamentVoting.objects.filter(parliament=Parliament.objects.get(pk=parl_pk), running=True).exists() \
            and votingRight \
            and not Bulletin.objects.filter(
        voting=ParliamentVoting.objects.get(parliament=Parliament.objects.get(pk=parl_pk), running=True),
        player=player).exists() \
            and Party.objects.filter(pk=party_pk).exists() \
            and regions_of_state.filter(pk=Party.objects.get(pk=party_pk).region.pk).exists() \
            and Party.objects.get(pk=party_pk).foundation_date < ParliamentVoting.objects.get(
        parliament=Parliament.objects.get(pk=parl_pk), running=True).voting_start:
        # создаем новый бюллетень голосования за переданного игрока
        vote = Bulletin(
            voting=ParliamentVoting.objects.get(parliament=Parliament.objects.get(pk=parl_pk), running=True),
            player=player,
            party=Party.objects.get(pk=party_pk))
        # сохраняем бюллетень
        vote.save()

    return redirect('government')
