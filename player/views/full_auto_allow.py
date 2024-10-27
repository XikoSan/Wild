from datetime import datetime, timedelta


from django.contrib.auth.decorators import login_required

from wild_politics.settings import JResponse
from player.decorators.player import check_player
from player.player import Player
from player.player_settings import PlayerSettings
from django.utils import translation
from django.utils.translation import ugettext as _
import re

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
                'response': _('Некорректное значение'),
                'header': _('Энергетики в авто-добыче'),
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
            'response': _('Ошибка метода'),
            'header': _('Энергетики в авто-добыче'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
