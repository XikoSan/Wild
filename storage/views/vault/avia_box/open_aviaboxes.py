import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.translation import pgettext
from player.decorators.player import check_player
from player.lootbox.lootbox import Lootbox
from player.player import Player
from player.player_settings import PlayerSettings
from storage.views.vault.avia_box.generate_rewards import generate_rewards
from wild_politics.settings import JResponse
from django.contrib.humanize.templatetags.humanize import number_format
from region.models.plane import Plane
from storage.models.lootbox_prize import LootboxPrize


# Открыть лутбоксы
@login_required(login_url='/')
@check_player
def open_aviaboxes(request):
    if request.method == "POST":
        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        if not Lootbox.objects.filter(player=player, stock__gt=0).exists():
            data = {
                'response': pgettext('open_box', 'У вас нет кейсов'),
                'header': pgettext('open_box', 'Открытие кейсов'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        lootboxes = Lootbox.objects.get(player=player)

        CashLog = apps.get_model('player.CashLog')

        spins, reward = generate_rewards()

        if reward > 0:
            player.cash += reward

            cash_log = CashLog(player=player, cash=reward, activity_txt='box')
            cash_log.save()

            player.save()

            reward = f'${number_format(reward)}'

        else:
            reward = 'ничего'

        lootboxes.stock -= 1
        lootboxes.opened += 1
        lootboxes.save()

        data = {
            'response': 'ok',
            'prizes': spins,
            'reward': reward,

            'boxes_count': lootboxes.stock,
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('open_box', 'Открытие кейсов'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
