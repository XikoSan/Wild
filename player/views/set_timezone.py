import pytz
import re
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.utils import translation
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from player.player_settings import PlayerSettings
from wild_politics.settings import JResponse


# Начать учет активности
@login_required(login_url='/')
@check_player
def set_timezone(request):
    if request.method == "POST":
        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        if request.POST.get('timezone') in pytz.common_timezones:
            player.time_zone = request.POST.get('timezone')

        else:
            data = {
                'response': _('Такого часового пояса в игре нет'),
                'header': _('Изменение часового пояса'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        player.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': _('Ошибка метода'),
            'header': _('Изменение часового пояса'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
