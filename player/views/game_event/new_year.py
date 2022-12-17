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
from player.game_event.global_part import GlobalPart
from player.player import Player
from django.utils.translation import ugettext as _
from django.utils.translation import pgettext

from ava_border.models.ava_border import AvaBorder


# главная страница
@login_required(login_url='/')
@check_player
def new_year(request):
    player = Player.get_instance(account=request.user)
    points = 0
    global_points = 0

    ava_border_1 = None
    ava_border_2 = None
    ava_border_3 = None

    if GameEvent.objects.filter(running=True, type='ny', event_start__lt=timezone.now(), event_end__gt=timezone.now()).exists():

        event = GameEvent.objects.filter(running=True, type='ny', event_start__lt=timezone.now(), event_end__gt=timezone.now()).first()

        if EventPart.objects.filter(player=player, event=event).exists():
            points = EventPart.objects.get(player=player, event=event).points

        if GlobalPart.objects.filter(event=event).exists():
            global_points = GlobalPart.objects.get(event=event).points

        if AvaBorder.objects.filter(pk=4).exists():
            ava_border_1 = AvaBorder.objects.get(pk=4)

        if AvaBorder.objects.filter(pk=5).exists():
            ava_border_2 = AvaBorder.objects.get(pk=5)

        if AvaBorder.objects.filter(pk=6).exists():
            ava_border_3 = AvaBorder.objects.get(pk=6)

    else:
        return redirect('overview')

    page = 'player/redesign/game_event/newyear.html'
    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext("game_event_ny", 'С новым годом!'),

        'player': player,
        'points': points,
        'global_points': global_points,

        'ava_border_1': ava_border_1,
        'ava_border_2': ava_border_2,
        'ava_border_3': ava_border_3,

    })

    return response
