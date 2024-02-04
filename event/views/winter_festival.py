import datetime
import json
import pytz
import random
import redis
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from player.decorators.player import check_player
from django.utils.translation import ugettext as _
from django.utils.translation import pgettext

from ava_border.models.ava_border import AvaBorder


# главная страница
@login_required(login_url='/')
@check_player
def winter_festival(request):
    Player = apps.get_model('player.Player')
    ActivityEvent = apps.get_model('event.ActivityEvent')
    ActivityEventPart = apps.get_model('event.ActivityEventPart')
    ActivityGlobalPart = apps.get_model('event.ActivityGlobalPart')

    player = Player.get_instance(account=request.user)
    points = 0
    global_points = 0

    if ActivityEvent.objects.filter(running=True, event_start__lt=timezone.now(), event_end__gt=timezone.now()).exists():

        event = ActivityEvent.objects.filter(running=True, event_start__lt=timezone.now(), event_end__gt=timezone.now()).first()

        if ActivityEventPart.objects.filter(player=player, event=event).exists():
            points = ActivityEventPart.objects.get(player=player, event=event).points

        if ActivityGlobalPart.objects.filter(event=event).exists():
            global_points = ActivityGlobalPart.objects.get(event=event).points
    else:
        return redirect('overview')

    page = 'event/festival.html'
    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext("game_event_ny", 'Зимний фестиваль'),

        'player': player,
        'points': points,
        'global_points': global_points,

    })

    return response
