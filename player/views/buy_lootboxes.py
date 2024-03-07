import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.lootbox.lootbox import Lootbox
from player.player import Player
from player.player_settings import PlayerSettings
from player.views.generate_rewards import generate_rewards
from wild_politics.settings import JResponse
from player.logs.gold_log import GoldLog

# Купить лутбоксы
@login_required(login_url='/')
@check_player
def buy_lootboxes(request):
    if request.method == "POST":
        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        try:
            buy_count = int(request.POST.get('count'))

        except ValueError:
            data = {
                'response': 'Некорректное количество сундуков для приобретения',
                'header': 'Приобретение сундуков',
                'grey_btn': _('Закрыть'),
            }
            return JResponse(data)

        today = timezone.now().date()
        was_buy = GoldLog.objects.filter(player=player, activity_txt='boxes', dtime__date=today).exists()

        if was_buy:
            data = {
                'response': 'Вы можете приобрести наборы сундуков только раз в день',
                'header': 'Приобретение сундуков',
                'grey_btn': _('Закрыть'),
            }
            return JResponse(data)

        if (buy_count == 50 or buy_count == 1000) and ( GoldLog.objects.filter(player=player, activity_txt='boxes', gold=40000).exists()\
                or GoldLog.objects.filter(player=player, activity_txt='boxes', gold=75000).exists() ):
            data = {
                'response': 'Вы можете приобрести большие наборы сундуков только единожды',
                'header': 'Приобретение сундуков',
                'grey_btn': _('Закрыть'),
            }
            return JResponse(data)

        buy_cost = buy_count * 1000

        if buy_count == 5:
            buy_cost = 4500

        if buy_count == 10:
            buy_cost = 8500

        if buy_count == 50:
            buy_cost = 40000

        if buy_count == 100:
            buy_cost = 75000

        if player.gold < buy_cost:
            data = {
                'response': 'Недостаточно золота для покупки',
                'header': 'Приобретение сундуков',
                'grey_btn': _('Закрыть'),
            }
            return JResponse(data)

        if Lootbox.objects.filter(player=player).exists():
            lboxes = Lootbox.objects.get(player=player)
            lboxes.stock += buy_count

        else:
            lboxes = Lootbox(player=player)
            lboxes.stock += buy_count

        lboxes.save()

        player.gold -= buy_cost
        player.save()

        GoldLog(player=player, gold=buy_cost, activity_txt='boxes').save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': _('Ошибка метода'),
            'header': _('Открытие сундуков'),
            'grey_btn': _('Закрыть'),
        }
        return JResponse(data)
