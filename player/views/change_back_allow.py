from datetime import datetime, timedelta


from django.contrib.auth.decorators import login_required

from wild_politics.settings import JResponse
from player.decorators.player import check_player
from player.player import Player
from player.player_settings import PlayerSettings
from django.utils import translation
from django.utils.translation import ugettext as _
import re

# Начать учет активности
@login_required(login_url='/')
@check_player
def change_back_allow(request):


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

        if request.POST.get('show_party_back') == 'true':
            player_settings.party_back = True

        elif request.POST.get('show_party_back') == 'false':
            player_settings.party_back = False

        else:
            data = {
                'response': _('Некорректное значение'),
                'header': _('Настройка партийного фона'),
                'grey_btn': _('Закрыть'),
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
            'header': _('Настройка партийного фона'),
            'grey_btn': _('Закрыть'),
        }
        return JResponse(data)
