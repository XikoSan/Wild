from datetime import datetime, timedelta


from django.contrib.auth.decorators import login_required

from wild_politics.settings import JResponse
from player.decorators.player import check_player
from player.player import Player
from player.player_settings import PlayerSettings
import re
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _

# Начать учет активности
@login_required(login_url='/')
@check_player
def color_change(request):


    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        color_back = request.POST.get('color_back')

        match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color_back)

        if not match:
            data = {
                'response': pgettext('profile', 'Некорректный код фона игры'),
                'header': pgettext('profile', 'Некорректный код цвета'),
                'grey_btn': _('Закрыть'),
            }
            return JResponse(data)

        color_block = request.POST.get('color_block')

        match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color_block)

        if not match:
            data = {
                'response': pgettext('profile', 'Некорректный код блоков игры'),
                'header': pgettext('profile', 'Некорректный код цвета'),
                'grey_btn': _('Закрыть'),
            }
            return JResponse(data)

        color_text = request.POST.get('color_text')

        match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color_text)

        if not match:
            data = {
                'response': pgettext('profile', 'Некорректный код текста игры'),
                'header': pgettext('profile', 'Некорректный код цвета'),
                'grey_btn': _('Закрыть'),
            }
            return JResponse(data)

        color_acct = request.POST.get('color_acct')

        match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color_acct)

        if not match:
            data = {
                'response': pgettext('profile', 'Некорректный код акцентов игры'),
                'header': pgettext('profile', 'Некорректный код цвета'),
                'grey_btn': _('Закрыть'),
            }
            return JResponse(data)


        if not PlayerSettings.objects.filter(player=player).exists():
            sett = PlayerSettings(
                player=player,
                color_back=color_back[1:],
                color_block=color_block[1:],
                color_text=color_text[1:],
                color_acct=color_acct[1:],
            )

            sett.save()

        else:
            sett = PlayerSettings.objects.get(player=player)

            sett.color_back =color_back[1:]
            sett.color_block=color_block[1:]
            sett.color_text =color_text[1:]
            sett.color_acct =color_acct[1:]

            sett.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка метода'),
            'header': pgettext('party_manage', 'Ошибка изменения цветов игры'),
            'grey_btn': _('Закрыть'),
        }
        return JResponse(data)
