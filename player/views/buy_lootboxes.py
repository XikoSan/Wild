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
