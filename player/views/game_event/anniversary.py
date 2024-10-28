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
from player.game_event.global_part import GlobalPart


# главная страница
@login_required(login_url='/')
@check_player
def anniversary(request):
    player = Player.get_instance(account=request.user)
    points = 0
    global_points = 0

    if GameEvent.objects.filter(running=True, type='av', event_start__lt=timezone.now(), event_end__gt=timezone.now()).exists():

        event = GameEvent.objects.filter(running=True, type='av', event_start__lt=timezone.now(), event_end__gt=timezone.now()).first()

        if EventPart.objects.filter(player=player, event=event).exists():
            points = EventPart.objects.get(player=player, event=event).points

        if GlobalPart.objects.filter(event=event).exists():
            global_points = GlobalPart.objects.get(event=event).points

    else:
        return redirect('overview')

    page = 'event/anniversary.html'
    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext("game_event", 'С годовщиной сервера Wild Politics!'),

        'player': player,
        'points': points,
        'global_points': global_points,

    })

    return response
