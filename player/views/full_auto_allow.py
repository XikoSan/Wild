import re
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.utils import translation
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from player.player_settings import PlayerSettings
from wild_politics.settings import JResponse


# Использовать Энергетики в авто-добыче
@login_required(login_url='/')
@check_player
def full_auto_allow(request):
    if request.method == "POST":
        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        player_settings = None

        # если у игрока есть настройки
        if PlayerSettings.objects.filter(player=player).exists():
            player_settings = PlayerSettings.objects.get(player=player)
        # иначе - создаем
        else:
            player_settings = PlayerSettings(player=player)

        if request.POST.get('full_auto') == 'true':
            player_settings.full_auto = True

        elif request.POST.get('full_auto') == 'false':
            player_settings.full_auto = False

        else:
            data = {
                'response': pgettext('full_auto', 'Некорректное значение'),
                'header': pgettext('full_auto', 'Энергетики в авто-добыче'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        player_settings.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('full_auto', 'Энергетики в авто-добыче'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
