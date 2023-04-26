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

        daily_limit = 15000 + (power * 100) + (knowledge * 100) + (endurance * 100)

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
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': ugettext('Ошибка метода'),
        }
        return JResponse(data)
