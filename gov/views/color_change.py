from datetime import datetime, timedelta


from django.contrib.auth.decorators import login_required

from wild_politics.settings import JResponse
from player.decorators.player import check_player
from player.player import Player
from party.party import Party
import re
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _
from state.models.parliament.deputy_mandate import DeputyMandate

# изменить цвет партии в парламенте
@login_required(login_url='/')
@check_player
def state_color_change(request):


    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        # если игрок действительно лидер партии
        if not DeputyMandate.objects.filter(player=player, is_president=True).exists():
            data = {
                'response': pgettext('edit_state_color', 'Вы не являетесь лидером государства'),
                'header': pgettext('edit_state_color', 'Цвет государства'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        state = DeputyMandate.objects.get(player=player, is_president=True).parliament.state

        party_color = request.POST.get('state_color')

        match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', party_color)

        if not match:
            data = {
                'response': pgettext('edit_state_color', 'Некорректный код цвета партии'),
                'header': pgettext('edit_state_color', 'Цвет государства'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        state.color = party_color[1:]
        state.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    else:
        data = {
            'response': pgettext('core', 'Ошибка метода'),
            'header': pgettext('edit_state_color', 'Цвет государства'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)

