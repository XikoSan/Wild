import datetime
import json
import pytz
import random
import redis
from datetime import timedelta
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import pgettext

from event.models.inviting_event.invite import Invite
from player.decorators.player import check_player
from django.db import connection
from event.models.inviting_event.cash_event import CashEvent
from player.logs.cash_log import CashLog


# главная страница
@login_required(login_url='/')
@check_player
def invited_list(request, pk):

    if not CashEvent.objects.filter(running=True, event_start__lt=timezone.now(),
                                    event_end__gt=timezone.now()).exists():
        return redirect('overview')

    event = CashEvent.objects.get(running=True, event_start__lt=timezone.now(),
                                    event_end__gt=timezone.now())

    Player = apps.get_model('player.Player')

    player = Player.get_instance(account=request.user)

    if not Player.objects.filter(pk=pk).exists():
        return redirect('overview')

    char = Player.get_instance(pk=pk)

    invited_list = Invite.objects.filter(sender=char, event=event)

    page = 'event/invited_list.html'
    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('game_event', "Приглашённые игроком %(nickname)s") % {"nickname": char.nickname},

        'player': player,
        'invited_list': invited_list,
    })

    return response
