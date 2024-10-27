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


# Открыть лутбоксы
@login_required(login_url='/')
@check_player
def open_lootboxes(request):
    if request.method == "POST":

        data = {
            'response': 'Открытие Сундуков невозможно сейчас',
            'header': 'Открытие сундуков',
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)

        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        if not Lootbox.objects.filter(player=player, stock__gt=0).exists():
            data = {
                'response': 'У вас нет новогодних сундуков',
                'header': 'Открытие сундуков',
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        try:
            open_count = int(request.POST.get('count'))

        except ValueError:
            data = {
                'response': 'Некорректное количество сундуков для открытия',
                'header': 'Открытие сундуков',
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        lootboxes = Lootbox.objects.get(player=player)

        if open_count > lootboxes.stock:
            data = {
                'response': 'Недостаточно сундуков для открытия',
                'header': 'Открытие сундуков',
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        gold_prize = 0
        prem_prize = 0
        wp_prize = 0

        GoldLog = apps.get_model('player.GoldLog')
        PremLog = apps.get_model('player.PremLog')
        WildpassLog = apps.get_model('player.WildpassLog')

        loop = 0
        for box in range(open_count):

            rewards, summs = generate_rewards(player)

            for reward in rewards:
                index = rewards.index(reward)

                if reward == 'gold':
                    player.gold += summs[index]
                    gold_prize += summs[index]

                    gold_log = GoldLog(player=player, gold=summs[index], activity_txt='bx_gld')
                    gold_log.save()

                if reward == 'premium':
                    if player.premium > timezone.now():
                        from_time = player.premium
                    else:
                        from_time = timezone.now()

                    player.premium = from_time + relativedelta(days=summs[index])
                    prem_prize += summs[index]

                    prem_log = PremLog(player=player, days=summs[index], activity_txt='lootbox')
                    prem_log.save()

                if reward == 'wild_pass':
                    player.cards_count += summs[index]
                    wp_prize += summs[index]

                    wp_log = WildpassLog(player=player, count=summs[index], activity_txt='lootbox')
                    wp_log.save()

        lootboxes.stock -= open_count
        lootboxes.save()

        player.save()

        if gold_prize == 0:
            gold_prize = ''

        if prem_prize == 0:
            prem_prize = ''

        if wp_prize == 0:
            wp_prize = ''

        data = {
            'response': 'ok',
            'gold_prize': gold_prize,
            'prem_prize': prem_prize,
            'wp_prize': wp_prize,

            'boxes_count': lootboxes.stock,
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
