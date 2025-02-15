import time
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from itertools import chain

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
def open_elections(request, parl_pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)
    # если есть такое парламент
    if not Parliament.objects.filter(pk=parl_pk).exists():
        return redirect('government')
    # если существуют АКТИВНЫЕ выборы
    if ParliamentVoting.objects.filter(parliament=Parliament.objects.get(pk=parl_pk), running=True).exists():
        vote = None
        # если игрок уже голосовал
        if Bulletin.objects.filter(
                voting=ParliamentVoting.objects.get(parliament=Parliament.objects.get(pk=parl_pk), running=True),
                player=player).exists():
            vote = Bulletin.objects.get(
                voting=ParliamentVoting.objects.get(parliament=Parliament.objects.get(pk=parl_pk), running=True),
                player=player)
        # регионы государства, в котором идут выборы
        state = Parliament.objects.get(pk=parl_pk).state
        # отсекаем регионы с военным положением
        martial_regions = Martial.objects.filter(active=True, days_left__gte=5, state=state).values_list('region__pk')
        mar_pk_list = []

        for m_reg in martial_regions:
            mar_pk_list.append(m_reg[0])

        regions_of_state = Region.objects.filter(state=state, joined_since__lt=ParliamentVoting.objects.get(
                                                    parliament=Parliament.objects.get(pk=parl_pk),
                                                    running=True).voting_start).exclude(pk__in=mar_pk_list)
        # для всех регионов государства
        # getting parties of state
        parties = None
        for regin in regions_of_state:
            more_parties = Party.objects.filter(region=regin,
                                                foundation_date__range=["1995-01-01", str(ParliamentVoting.objects.get(
                                                    parliament=Parliament.objects.get(pk=parl_pk),
                                                    running=True).voting_start)],
                                                deleted=False)
            if not parties:
                parties = more_parties
            else:
                parties = list(chain(parties, more_parties))

        # право голосовать на текущих выборах.
        # Появляется, если с момента взятия прописки прошли сутки
        # А также если в регионе прописки нет военного положения
        votingRight = None
        regions_of_state = Region.objects.filter(state=state)
        if regions_of_state.filter(pk=player.residency.pk).exists() \
                and player.residency_date + timedelta(days=1) < timezone.now() \
                and player.power + player.knowledge + player.endurance >= 10:
            votingRight = True

        remain = interval_in_seconds(
            ParliamentVoting.objects.get(parliament=Parliament.objects.get(pk=parl_pk), running=True),
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
        return render(request, 'state/redesign/elections.html',
                      {'player': player,
                       'partys': parties,
                       'state': state,
                       'vote': vote,
                       'remain': remain,
                       'time_text': time_text,
                       'parliament': Parliament.objects.get(pk=parl_pk),
                       'votingRight': votingRight
                       })
    else:
        return redirect('government')
