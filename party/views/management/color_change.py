from datetime import datetime, timedelta


from django.contrib.auth.decorators import login_required

from wild_politics.settings import JResponse
from player.decorators.player import check_player
from player.player import Player
from party.party import Party
import re
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _

# изменить цвет партии в парламенте
@login_required(login_url='/')
@check_player
def party_color_change(request):


    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        if player.party_post:
            # если игрок действительно лидер партии
            if player.party_post.party_lead:

                changing_party = Party.objects.get(pk=player.party.pk)

                party_color = request.POST.get('party_color')

                match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', party_color)

                if not match:
                    data = {
                        'response': pgettext('party_manage', 'Некорректный код цвета партии'),
                        'header': pgettext('profile', 'Некорректный код цвета'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JResponse(data)

                changing_party.color = party_color[1:]
                changing_party.save()

                data = {
                    'response': 'ok',
                }
                return JResponse(data)

            else:
                data = {
                    'response': pgettext('party_manage', 'Вы не являетесь лидером партии'),
                    'header': pgettext('party_manage', 'Ошибка изменения цвета партии'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)
        else:
            data = {
                'response': pgettext('party_manage', 'Вы не состоите в партии'),
                'header': pgettext('party_manage', 'Ошибка изменения цвета партии'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)
    else:
        data = {
            'response': pgettext('core', 'Ошибка метода'),
            'header': pgettext('party_manage', 'Ошибка изменения цветов игры'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)

