# coding=utf-8
# import operator
# from datetime import timedelta
# from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.player import Player
from wild_politics.settings import JResponse
from django.utils.translation import ugettext
from django.utils.translation import pgettext
from django.apps import apps
from django.utils import timezone
from django.db import connection


# получение денег с дейлика
@login_required(login_url='/')
@check_player
def daily_status(request):
    if request.method == "GET":

        player = Player.get_instance(account=request.user)

        # лимит денег, доступный игроку
        power = player.power
        if power > 100:
            power = 100

        knowledge = player.knowledge
        if knowledge > 100:
            knowledge = 100

        endurance = player.endurance
        if endurance > 100:
            endurance = 100

        daily_limit = 20000 + (power * 100) + (knowledge * 100) + (endurance * 100)

        # ------------------

        CashEvent = apps.get_model('event.CashEvent')
        bonus = 0

        if CashEvent.objects.filter(running=True, event_start__lt=timezone.now(),
                                    event_end__gt=timezone.now()).exists():
            cursor = connection.cursor()

            cursor.execute(
                f'SELECT event_invite.sender_id,SUM(player_player.endurance+player_player.knowledge+player_player.power-event_invite.exp)AS total_stats FROM public.event_invite INNER JOIN public.player_player ON event_invite.invited_id=player_player.id WHERE sender_id = {player.pk} GROUP BY event_invite.sender_id ORDER BY total_stats DESC limit 1;')

            raw_top = cursor.fetchall()

            if raw_top:
                bonus = raw_top[0][1] // 10

        if bonus > 0:
            daily_limit = int(daily_limit * (1 + (bonus / 100)))

        # ------------------        

        # бонус по выходным
        if timezone.now().date().weekday() == 5 or timezone.now().date().weekday() == 6:
            daily_limit = daily_limit * 2

        daily_energy_limit = 0
        if player.energy_limit - player.paid_consumption > 0:
            daily_energy_limit = player.energy_limit - player.paid_consumption

        # 3500 - количество энергии, которую надо выфармить за день
        if player.paid_consumption >= player.energy_limit:
            daily_procent = 100
        else:
            daily_procent = player.energy_consumption / ((player.energy_limit - player.paid_consumption) / 100)

        if daily_procent > 100:
            daily_procent = 100

        # сумма, которую уже можно забрать
        daily_current_sum = int((daily_limit - player.paid_sum) / 100 * daily_procent)

        data = {
            'energy_consumption': player.energy_consumption,
            'daily_energy_limit': daily_energy_limit,
            'daily_current_sum': daily_current_sum,
            'daily_procent': daily_procent,
        }
        return JResponse(data)

    else:
        data = {
            'header': ugettext('Ошибка метода'),
            'grey_btn': pgettext('core', 'Закрыть'),
            'response': ugettext('Ошибка метода'),
        }
        return JResponse(data)
