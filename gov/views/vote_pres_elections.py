from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone

from gov.models.president import President
from gov.models.presidential_voting import PresidentialVoting
from gov.models.vote import Vote
from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from region.models.region import Region
from state.models.parliament.bulletin import Bulletin
from state.models.parliament.parliament import Parliament
from state.models.parliament.parliament_voting import ParliamentVoting


# проголосовать на выборах в парламент государства
@login_required(login_url='/')
@check_player
def vote_pres_elections(request, pres_pk, cand_pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    president_post = President.objects.get(pk=pres_pk)

    # право голосовать на текущих выборах.
    # Появляется, если с момента взятия прописки прошли сутки
    votingRight = False
    regions_of_state = Region.objects.filter(state=president_post.state)
    if regions_of_state.filter(pk=player.residency.pk).exists() \
            and player.residency_date + timedelta(days=1) < timezone.now():
        votingRight = True

    # если у игрока есть прописка в государстве,
    #  а также существуют АКТИВНЫЕ выборы,
    #  у него есть право на них голосовать
    #  и он на этих выборах ещё не голосовал
    #  существует такой кандадат
    #  и он находится в списке кандидатов на выборах
    if regions_of_state.filter(pk=player.residency.pk).exists() \
            and PresidentialVoting.objects.filter(president=president_post, running=True).exists() \
            and votingRight \
            and not Vote.objects.filter(
        voting=PresidentialVoting.objects.get(president=president_post, running=True),
        player=player).exists() \
            and Player.objects.filter(pk=cand_pk).exists() \
            and Player.get_instance(pk=cand_pk) in PresidentialVoting.objects.get(president=president_post, running=True).candidates.all():

        # создаем новый бюллетень голосования за переданного игрока
        vote = Vote(
            voting=PresidentialVoting.objects.get(president=president_post, running=True),
            player=player,
            challenger=Player.get_instance(pk=cand_pk)
        )
        # сохраняем бюллетень
        vote.save()

    return redirect('government')
