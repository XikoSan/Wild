from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import JResponse
import datetime
from django.apps import apps


# изучить навык
@login_required(login_url='/')
@check_player
@transaction.atomic
def use_card(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        header = 'Активация премиум-аккаунта'
        if player.premium > timezone.now():
            header = 'Продление премиум-аккаунта'

        if not player.cards_count > 0:
            data = {
                # 'response': _('positive_enrg_req'),
                'response': 'Недостаточно карт Wild Pass. Приобретите их у Администрации',
                'header': header,
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        WildpassLog = apps.get_model('player.WildpassLog')
        GoldLog = apps.get_model('player.GoldLog')
        PremLog = apps.get_model('player.PremLog')

        # активация ради золота
        if int(request.POST.get('gold_usage')) == 1:
            # начисляем золото
            player.gold += 800

            gold_log = GoldLog(player=player, gold=800, activity_txt='wpass')
            gold_log.save()

        else:
            # время, к которому прибавляем месяц
            if player.premium > timezone.now():
                from_time = player.premium
            else:
                from_time = timezone.now()

            player.premium = from_time + relativedelta(months=1)

            prem_log = PremLog(player=player, days=30, activity_txt='wpass')
            prem_log.save()

        player.cards_count -= 1
        player.save()

        wp_log = WildpassLog(player=player, count=-1, activity_txt='using')
        wp_log.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            # 'response': _('positive_enrg_req'),
            'response': 'Ошибка типа запроса',
            'header': 'Изучение навыка',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
