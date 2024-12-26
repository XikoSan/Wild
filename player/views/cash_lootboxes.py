import pytz
import re
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils import translation
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

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "lootboxes_channel",  # Группа, к которой подключены клиенты
            {
                "type": "broadcast_purchase",
                "value": ceil(jp.amount / 2),
            }
        )

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
