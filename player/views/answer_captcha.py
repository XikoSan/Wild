import re
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from player.player_settings import PlayerSettings
from wild_politics.settings import JResponse


# Начать учет активности
@login_required(login_url='/')
@check_player
def answer_captcha(request):
    if request.method == "POST":
        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        # если у игрока есть настройки
        if PlayerSettings.objects.filter(player=player).exists():
            player_settings = PlayerSettings.objects.get(player=player)

            answer = int(request.POST.get('answer'))

            if not player_settings.captcha_ans == answer:
                player_settings.captcha_ans = 0
                player_settings.save()

                data = {
                    'response': _('Неправильный ответ'),
                    'header': _('Ответ на Captcha'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)

            player_settings.captcha_date = timezone.now()
            player_settings.captcha_ans = 0
            player_settings.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': _('Ошибка метода'),
            'header': _('Ответ на Captcha'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
