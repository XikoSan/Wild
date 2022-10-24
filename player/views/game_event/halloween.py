import datetime
import json
import pytz
import random
import redis
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from player.decorators.player import check_player
from player.game_event.game_event import GameEvent
from player.game_event.event_part import EventPart
from player.player import Player
from django.utils.translation import ugettext as _
from django.utils.translation import pgettext

from ava_border.models.ava_border import AvaBorder


# главная страница
@login_required(login_url='/')
@check_player
def halloween(request):
    player = Player.get_instance(account=request.user)
    points = 0

    ava_border_1 = None
    ava_border_2 = None
    ava_border_3 = None

    if GameEvent.objects.filter(running=True, event_start__lt=timezone.now(), event_end__gt=timezone.now()).exists():

        event = GameEvent.objects.filter(running=True, event_start__lt=timezone.now(), event_end__gt=timezone.now()).first()

        if EventPart.objects.filter(player=player, event=event).exists():
            points = EventPart.objects.get(player=player, event=event).points

        if AvaBorder.objects.filter(pk=1).exists():
            ava_border_1 = AvaBorder.objects.get(pk=1)

        if AvaBorder.objects.filter(pk=2).exists():
            ava_border_2 = AvaBorder.objects.get(pk=2)

        if AvaBorder.objects.filter(pk=3).exists():
            ava_border_3 = AvaBorder.objects.get(pk=3)

    else:
        return redirect('overview')

    page = 'player/redesign/game_event/halloween.html'
    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext("game_event", 'Хэллоуинский ивент!'),

        'player': player,
        'points': points,

        'ava_border_1': ava_border_1,
        'ava_border_2': ava_border_2,
        'ava_border_3': ava_border_3,

    })

    return response
