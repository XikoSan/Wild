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


# получение денег с дейлика
@login_required(login_url='/')
@check_player
@transaction.atomic
def retrieve_cash(request):
    if request.method == "POST":

        player = Player.objects.get(account=request.user)

        failure, sum = player.daily_claim()

        if failure:
            return failure

        else:
            cash_log = CashLog(player=player, cash=sum, activity_txt='daily')
            cash_log.save()

            data = {
                'response': 'ok',
            }
            return JResponse(data)

    else:
        data = {
            'header': 'Ошибка получения финансирования',
            'grey_btn': 'Закрыть',
            'response': 'Ты уверен что тебе сюда, путник?',
        }
        return JResponse(data)
