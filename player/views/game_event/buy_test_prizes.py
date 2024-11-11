import pytz
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext as _
from math import ceil

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.logs.gold_log import GoldLog
from player.logs.prem_log import PremLog
from player.logs.test_log import TestLog
from player.logs.freebie_usage import FreebieUsage
from player.player import Player
from region.models.plane import Plane
from wild_politics.settings import JResponse
from django.utils.translation import pgettext

# Получить халяву
@login_required(login_url='/')
@check_player
def get_freebie(request):
    if request.method == "POST":

        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        type = request.POST.get('type')

        if type not in ['cash_500k',]:
            data = {
                'response': pgettext('shop', 'Некорректно указан товар'),
                'header': pgettext('shop', 'Получение бонуса'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if FreebieUsage.objects.filter(player=player, type=type).exists():
            data = {
                'response': pgettext('shop', 'Этот товар уже куплен вами'),
                'header': pgettext('shop', 'Получение бонуса'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        # --------------------------------------

        if type == 'cash_500k':

            user_agent = request.META.get('HTTP_USER_AGENT', '')

            if "WildPoliticsApp" in user_agent:
                import re
                match = re.search(r"WildPoliticsApp_(\d+\.\d+\.\d+)", user_agent)
                if match:
                    if match.group(1) != '1.5.3':
                        data = {
                            'response': pgettext('shop', 'Ошибка версии приложения'),
                            'header': pgettext('shop', 'Получение бонуса'),
                            'grey_btn': pgettext('core', 'Закрыть'),
                        }
                        return JResponse(data)

            player.cash += 500000
            player.save()

            CashLog.create(player=player, cash=500000, activity_txt='bonus')

        usage = FreebieUsage(
            player=player,
            type=type,
        )
        usage.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка метода'),
            'header': pgettext('shop', 'Получение бонуса'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
