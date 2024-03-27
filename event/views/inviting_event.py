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
from django.utils.translation import ugettext as _

from event.models.inviting_event.invite import Invite
from player.decorators.player import check_player
from django.db import connection
from event.models.inviting_event.cash_event import CashEvent



# главная страница
@login_required(login_url='/')
@check_player
def inviting_event(request):

    if not CashEvent.objects.filter(running=True, event_start__lt=timezone.now(),
                                    event_end__gt=timezone.now()).exists():
        return redirect('overview')

    Player = apps.get_model('player.Player')

    player = Player.get_instance(account=request.user)

    invited = False

    if request.user.date_joined + timedelta(days=3) < timezone.now() \
            or Invite.objects.filter(invited=player).exists():
        invited = True

    invited_list = Invite.objects.filter(sender=player)
    total_bonus = 0
    cash_reward = None

    for line in invited_list:
        total_bonus += line.invited.power + line.invited.knowledge +  + line.invited.endurance

    total_bonus = total_bonus // 10

    cursor = connection.cursor()

    cursor.execute('SELECT event_invite.sender_id,SUM(player_player.endurance+player_player.knowledge+player_player.power)AS total_stats FROM public.event_invite INNER JOIN public.player_player ON event_invite.invited_id=player_player.id GROUP BY event_invite.sender_id ORDER BY total_stats DESC limit 10;')
    raw_top = cursor.fetchall()

    top_pk_list = []
    top_dict = {}

    top_players = []

    for line in raw_top:
        top_pk_list.append(line[0])

        top_dict[line[0]] = line[1]

    top_players_raw = Player.objects.filter(pk__in=top_pk_list)

    top = 1
    for line in raw_top:
        char = top_players_raw.get(pk=int(line[0]))
        top_players.append(char)

        if top == 1 and char == player:
            cash_reward = 3000

        if top == 2 and char == player:
            cash_reward = 2000

        if top == 3 and char == player:
            cash_reward = 1000

        top += 1


    page = 'event/inviting.html'
    # отправляем в форму
    response = render(request, page, {
        'page_name': 'Пригласи друга!',

        'player': player,

        'invited': invited,

        'invited_list': invited_list,
        'total_bonus': total_bonus,
        'cash_reward': cash_reward,

        'top_players': top_players,
        'top_dict': top_dict,

    })

    return response
