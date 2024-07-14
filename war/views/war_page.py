from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from itertools import chain

from player.decorators.player import check_player
from player.player import Player
from player.views.get_subclasses import get_subclasses
from player.views.timers import interval_in_seconds
from region.models.region import Region
from war.models.wars.war import War

from war.models.wars.revolution.rebel import Rebel


# страница войн
@login_required(login_url='/')
@check_player
def war_page(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    wars_list = []
    state_wars_list = []
    war_countdowns = {}

    kwargs_q1 = {}
    kwargs_q2 = {}

    if player.region.state:
        state_regions = Region.objects.filter(state=player.region.state)
        kwargs_q1['agr_region__in'] = state_regions
        kwargs_q2['def_region__in'] = state_regions

    else:
        kwargs_q1['agr_region'] = player.region
        kwargs_q2['def_region'] = player.region

    war_types = get_subclasses(War)
    for type in war_types:

        # если есть активные войны этого типа
        if type.objects.filter(running=True, deleted=False).exists():
            # если лист на вывод не пустой
            if wars_list:
                # добавляем в список на вывод
                wars_list = list(chain(wars_list, type.objects.filter(running=True, deleted=False)))
            else:
                wars_list = type.objects.filter(running=True, deleted=False)

        # если есть активные войны, связанные с нашим госом
        if type.objects.filter(running=True, deleted=False).filter(Q(**kwargs_q1) | Q(**kwargs_q2)).exists():
            # если лист на вывод не пустой
            if state_wars_list:
                # добавляем в список на вывод
                state_wars_list = list(chain(state_wars_list, type.objects.filter(running=True, deleted=False).filter(
                    Q(**kwargs_q1) | Q(**kwargs_q2))))
            else:
                state_wars_list = type.objects.filter(running=True, deleted=False).filter(
                    Q(**kwargs_q1) | Q(**kwargs_q2))

    for war in wars_list:
        if not war in war_countdowns.keys():
            war_countdowns[war] = interval_in_seconds(
                object=war,
                start_fname='start_time',
                end_fname=None,
                delay_in_sec=86400
            )
    for war in state_wars_list:
        if not war in war_countdowns.keys():
            war_countdowns[war] = interval_in_seconds(
                object=war,
                start_fname='start_time',
                end_fname=None,
                delay_in_sec=86400
            )

# -------------------------

    rebels = Rebel.actual.filter(region=player.region)
    rebels_count = rebels.count()

    rebel_price = 500
    if player.region == player.residency:
        rebel_price = 300

    # отправляем в форму
    return render(request, 'war/redesign/war_page.html', {
        # самого игрока
        'player': player,
        # список войн
        'wars_list': wars_list,
        # список войн госа
        'state_wars_list': state_wars_list,
        # таймеры отсчета для обоих списков
        'war_countdowns': war_countdowns,
        # повстанцы в этом регионе
        'rebels': rebels,
        'rebels_count': rebels_count,
        'rebel_price': rebel_price,

    })
