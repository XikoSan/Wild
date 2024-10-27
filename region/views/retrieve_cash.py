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
@transaction.atomic
def retrieve_cash(request):
    if request.method == "POST":

        player = Player.get_instance(account=request.user)

        failure, sum = player.daily_claim()

        if failure:
            return failure

        else:
            CashLog.create(player=player, cash=sum, activity_txt='daily')

            data = {
                'response': 'ok',
            }
            return JResponse(data)

    else:
        data = {
            'header': pgettext('mining', 'Ошибка получения финансирования'),
            'grey_btn': pgettext('core', 'Закрыть'),
            'response': ugettext('Ошибка метода'),
        }
        return JResponse(data)
