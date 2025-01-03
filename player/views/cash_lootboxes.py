import json
import pytz
import re
import redis
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from django.utils import translation
from django.utils.timezone import now, timedelta
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _
from math import ceil

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.logs.gold_log import GoldLog
from player.lootbox.jackpot import Jackpot
from player.lootbox.lootbox import Lootbox
from player.player import Player
from player.player_settings import PlayerSettings
from player.views.generate_rewards import generate_rewards
from storage.models.lootbox_coauthors import LootboxCoauthor
from storage.views.vault.avia_box.generate_rewards import prepare_plane_lists
from wild_politics.settings import JResponse


# Купить лутбоксы
@login_required(login_url='/')
@check_player
def cash_lootboxes(request):
    if request.method == "POST":

        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        # Определяем временной диапазон за последние сутки
        last_24_hours = now() - timedelta(days=1)

        # Суммируем значение поля 'cash' для указанных условий
        total_cash = CashLog.objects.filter(
            player=player,
            activity_txt='buy_box',
            dtime__gte=last_24_hours
        ).aggregate(Sum('cash'))['cash__sum']

        # Если сумма отсутствует, она равна 0
        if total_cash is None:
            total_cash = 0

        if total_cash <= -10000000:
            data = {
                'response': 'Исчерпаны покупки лутбоксов за деньги. Подождите немного',
                'header': 'Приобретение сундуков',
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        try:
            buy_count = int(request.POST.get('count'))

        except ValueError:
            data = {
                'response': 'Некорректное количество сундуков для приобретения',
                'header': 'Приобретение сундуков',
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if buy_count <= 0:
            data = {
                'response': 'Некорректное количество сундуков для приобретения',
                'header': 'Приобретение сундуков',
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        buy_cost = buy_count * 100000

        if player.cash < buy_cost:
            data = {
                'response': 'Недостаточно средств для покупки',
                'header': 'Приобретение сундуков',
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        # from player.logs.print_log import log
        # log(total_cash)
        # log(buy_cost)

        if total_cash - buy_cost < -10000000:
            data = {
                'response': f'На данный момент, вам доступно для покупки только {int((10000000 + total_cash) / 100000)} сундуков',
                'header': 'Приобретение сундуков',
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if Lootbox.objects.filter(player=player).exists():
            lboxes = Lootbox.objects.get(player=player)
            lboxes.stock += buy_count

        else:
            lboxes = Lootbox(player=player)
            lboxes.stock += buy_count

        lboxes.save()

        player.cash -= buy_cost
        player.save()

        CashLog(player=player, cash=0 - buy_cost, activity_txt='buy_box').save()

        if not Jackpot.objects.filter(amount__gt=200000).exists():
            jp = Jackpot(amount=10000000)

        else:
            jp = Jackpot.objects.filter(amount__gt=200000).first()

        jp.amount += buy_cost
        jp.save()

        # ----------------------------------------

        # redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
        #
        # key = f'boxes_{player.pk}'
        #
        # # Получение текущих данных игрока
        # data = redis_client.get(key)
        # if data:
        #     player_data = json.loads(data)
        # else:
        #     player_data = {"expense": 0, "income": 0}
        #
        # # Обновление данных
        # player_data["expense"] += buy_cost
        #
        # # Сохранение обратно в Redis
        # redis_client.set(key, json.dumps(player_data))

        # ----------------------------------------

        # channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)(
        #     "lootboxes_channel",  # Группа, к которой подключены клиенты
        #     {
        #         "type": "broadcast_purchase",
        #         "value": ceil(jp.amount / 2),
        #     }
        # )

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': _('Ошибка метода'),
            'header': _('Открытие сундуков'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
