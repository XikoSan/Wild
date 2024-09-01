import time
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from itertools import chain

from gov.models.president import President
from gov.models.presidential_voting import PresidentialVoting
from gov.models.vote import Vote
from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from player.views.timers import interval_in_seconds
from region.models.region import Region
from state.models.parliament.bulletin import Bulletin
from state.models.parliament.parliament import Parliament
from state.models.parliament.parliament_voting import ParliamentVoting
from war.models.martial import Martial


# открытие страницы выборов
@login_required(login_url='/')
@check_player
def open_pres_elections(request, pres_pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)
    # проверяем, есть ли такой пост президента
    if not President.objects.filter(pk=pres_pk).exists():
        return redirect('government')

    president = President.objects.get(pk=pres_pk)

    # если существуют АКТИВНЫЕ выборы
    if PresidentialVoting.objects.filter(president=president, running=True).exists():

        voting = PresidentialVoting.objects.get(president=president, running=True)

        vote = None
        # если игрок уже голосовал
        if Vote.objects.filter(
                voting=voting,
                player=player
        ).exists():
            vote = Vote.objects.get(
                voting=voting,
                player=player
            )

        # право голосовать на текущих выборах.
        # Появляется, если с момента взятия прописки прошли сутки
        # А также если в регионе прописки нет военного положения
        votingRight = None
        # отсекаем регионы с военным положением
        martial_regions = Martial.objects.filter(active=True, days_left__gte=5, state=president.state).values_list('region__pk')
        mar_pk_list = []

        for m_reg in martial_regions:
            mar_pk_list.append(m_reg[0])

        regions_of_state = Region.objects.filter(state=president.state).exclude(pk__in=mar_pk_list)

        if regions_of_state.filter(pk=player.residency.pk).exists() \
                and player.residency_date + timedelta(days=1) < timezone.now():
            votingRight = True

        remain = interval_in_seconds(
            voting,
            'voting_start',
            end_fname=None,
            delay_in_sec=86400
            # delay_in_sec=60
        )

        time_text = None
        if remain > 0:
            time_text = time.strftime('%H:%M:%S', time.gmtime(remain))
        else:
            return redirect('government')

        # отправляем в форму
        return render(request, 'gov/redesign/elections.html',
                      {'player': player,
                       'candidates': voting.candidates.all(),
                       'president': president,
                       'state': president.state,
                       'vote': vote,
                       'remain': remain,
                       'time_text': time_text,
                       'votingRight': votingRight
                       })
    else:
        return redirect('government')
