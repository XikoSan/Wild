from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import JResponse
import datetime


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

        # активация ради золота
        if int(request.POST.get('gold_usage')) == 1:
            if datetime.datetime.now() > datetime.datetime(2024, 6, 1, 0, 0):
                player.gold += 800
            else:
                player.gold += 1000

        else:
            # время, к которому прибавляем месяц
            if player.premium > timezone.now():
                from_time = player.premium
            else:
                from_time = timezone.now()

            player.premium = from_time + relativedelta(months=1)

        player.cards_count -= 1
        player.save()

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
