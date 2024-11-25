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


# Начать учет активности
@login_required(login_url='/')
@check_player
def set_language(request):
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

        if translation.check_for_language(request.POST.get('lang')):
            player_settings.language = request.POST.get('lang')

        else:
            data = {
                'response': pgettext('set_language', 'Такого языка в игре нет'),
                'header': pgettext('set_language', 'Изменение языка'),
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
            'header': pgettext('set_language', 'Изменение языка'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
