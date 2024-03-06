import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils import translation
from django.db import transaction
from django.utils.translation import ugettext as _
from django.contrib.humanize.templatetags.humanize import number_format

from player.bonus_code.bonus_code import BonusCode
from player.bonus_code.code_usage import CodeUsage
from player.decorators.player import check_player
from player.player import Player
from player.logs.prem_log import PremLog
from player.logs.gold_log import GoldLog
from player.player_settings import PlayerSettings
from player.views.generate_rewards import generate_rewards
from wild_politics.settings import JResponse
from dateutil.relativedelta import relativedelta
from player.logs.wildpass_log import WildpassLog
from player.views.set_cah_log import set_cash_log


# Открыть лутбоксы
@login_required(login_url='/')
@check_player
@transaction.atomic
def activate_code(request):
    if request.method == "POST":

        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        if not BonusCode.objects.filter(
                                        code=request.POST.get('code'),
                                        date__gt=timezone.now()
                                        ).exists():
            data = {
                'response': 'Указанный код не существует или истёк',
                'header': _('Активация кода'),
                'grey_btn': _('Закрыть'),
            }
            return JResponse(data)

        code = BonusCode.objects.get(code=request.POST.get('code'), date__gt=timezone.now())

        if code.reusable:
            if CodeUsage.objects.filter(code=code, player=player).exists():
                data = {
                    'response': 'Данный код уже был вами активирован',
                    'header': _('Активация кода'),
                    'grey_btn': _('Закрыть'),
                }
                return JResponse(data)

        else:
            if CodeUsage.objects.filter(code=code).exists():
                data = {
                    'response': 'Данный код уже был активирован',
                    'header': _('Активация кода'),
                    'grey_btn': _('Закрыть'),
                }
                return JResponse(data)

        text = None

        # премиум-аккаунт
        if code.premium > 0:
            # время, к которому прибавляем месяц
            if player.premium > timezone.now():
                from_time = player.premium
            else:
                from_time = timezone.now()

            player.premium = from_time + relativedelta(days=code.premium)

            prem_log = PremLog(player=player, days=30, activity_txt='bonus')
            prem_log.save()

            text = f'премиум-дни: {code.premium}'

        # золото
        if code.gold > 0:
            player.gold += code.gold

            gold_log = GoldLog(player=player, gold=code.gold, activity_txt='bonus')
            gold_log.save()

            if text:
                text += f', золото: {code.gold}'
            else:
                text = f'золото: {code.gold}'

        # вилдпасс
        if code.wild_pass > 0:
            player.cards_count += code.wild_pass

            WildpassLog = apps.get_model('player.WildpassLog')
            wp_log = WildpassLog(player=player, count=code.wild_pass, activity_txt='bonus')
            wp_log.save()

            if text:
                text += f', Wild Pass: {code.wild_pass}'
            else:
                text = f'Wild Pass: {code.wild_pass}'


        # деньги
        if code.cash > 0:
            player.cash += code.cash

            set_cash_log(player, code.cash, 'bonus', timezone.now())

            if text:
                text += f', деньги: {number_format(code.cash)}'
            else:
                text += f'деньги: {number_format(code.cash)}'

        player.save()

        usage = CodeUsage(code=code, player=player)
        usage.save()

        if not text:
            text = ''

        text = 'Код активирован! Вы получили: ' + text

        data = {
            'response': 'ok',

            'header': _('Активация кода'),
            'text': text,
            'grey_btn': _('Закрыть'),
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': _('Ошибка метода'),
            'header': _('Активация кода'),
            'grey_btn': _('Закрыть'),
        }
        return JResponse(data)
