import pytz
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext as _
from math import ceil

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.logs.gold_log import GoldLog
from player.logs.prem_log import PremLog
from player.logs.test_point_usage import TestPointUsage
from player.player import Player
from region.models.plane import Plane
from wild_politics.settings import JResponse
from player.logs.test_log import TestLog


# Купить лутбоксы
@login_required(login_url='/')
@check_player
def buy_test_prizes(request):
    if request.method == "POST":

        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        type = request.POST.get('type')

        if type not in ['7_prem', 'plane', 'cash', 'gold', 'wildpass', '30_prem']:
            data = {
                'response': 'Некорректно указан товар',
                'header': 'Покупка за очки тестирования',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if TestPointUsage.objects.filter(player=player, type=type).exists():
            data = {
                'response': 'Этот товар уже куплен вами',
                'header': 'Покупка за очки тестирования',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        points_before = 0
        points_used = 0

        if TestLog.objects.filter(player=player).exists():
            points_before = TestLog.objects.filter(player=player).count()

        if TestPointUsage.objects.filter(player=player).exists():
            usages = TestPointUsage.objects.filter(player=player)

            for usage in usages:
                points_used += usage.count

        if points_before - points_used <= 0:
            data = {
                'response': 'Вы израсходовали очки',
                'header': 'Покупка за очки тестирования',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        # --------------------------------------

        points = 0

        if type == '7_prem':

            if points_before - points_used < 1:
                data = {
                    'response': 'Недостаточно очков',
                    'header': 'Покупка за очки тестирования',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

            # время, к которому прибавляем месяц
            if player.premium > timezone.now():
                from_time = player.premium
            else:
                from_time = timezone.now()

            player.premium = from_time + relativedelta(days=7)

            player.save()

            prem_log = PremLog(player=player, days=7, activity_txt='bonus')
            prem_log.save()

            points = 1

        # --------------------------------------

        if type == 'plane':

            if points_before - points_used < 3:
                data = {
                    'response': 'Недостаточно очков',
                    'header': 'Покупка за очки тестирования',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

            plane = Plane(
                player=player,
                plane='sailor',
                color='android'
            )
            plane.save()

            points = 3

        # --------------------------------------

        if type == 'cash':

            if points_before - points_used < 5:
                data = {
                    'response': 'Недостаточно очков',
                    'header': 'Покупка за очки тестирования',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

            player.cash += 100000
            player.save()

            CashLog.create(player=player, cash=100000, activity_txt='bonus')

            points = 5

        # --------------------------------------

        if type == 'gold':

            if points_before - points_used < 9:
                data = {
                    'response': 'Недостаточно очков',
                    'header': 'Покупка за очки тестирования',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

            player.gold += 1000
            player.save()

            goldlog = GoldLog(player=player, gold=1000, activity_txt='bonus')
            goldlog.save()

            points = 9

        # --------------------------------------

        if type == 'wildpass':

            if points_before - points_used < 11:
                data = {
                    'response': 'Недостаточно очков',
                    'header': 'Покупка за очки тестирования',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

            player.cards_count += 1
            player.save()

            WildpassLog = apps.get_model('player.WildpassLog')
            wp_log = WildpassLog(player=player, count=1, activity_txt='bonus')
            wp_log.save()

            points = 11

        # --------------------------------------

        if type == '30_prem':

            if points_before - points_used < 10:
                data = {
                    'response': 'Недостаточно очков',
                    'header': 'Покупка за очки тестирования',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

            # время, к которому прибавляем месяц
            if player.premium > timezone.now():
                from_time = player.premium
            else:
                from_time = timezone.now()

            player.premium = from_time + relativedelta(months=1)

            player.save()

            prem_log = PremLog(player=player, days=30, activity_txt='bonus')
            prem_log.save()

            points = 10

        # --------------------------------------

        usage = TestPointUsage(
            player=player,
            type=type,
            count=points,
        )
        usage.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': 'Ошибка метода',
            'header': 'Покупка за очки тестирования',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
