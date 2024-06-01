from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from region.models.plane import Plane
from wild_politics.settings import JResponse


@login_required(login_url='/')
@check_player
# установить позывной
def set_plane_nick(request):
    if request.method == "POST":
        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        nickname = request.POST.get('plane_nick')

        if nickname == '':
            data = {
                'response': 'Позывной не может быть пустым',
                'header': 'Установить позывной',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        try:
            plane_id = int(request.POST.get('plane_id'))

        except ValueError:
            data = {
                'header': 'Установить позывной',
                'grey_btn': 'Закрыть',
                'response': 'ID техники должен быть целым числом',
            }
            return JResponse(data)

        # дефолтного
        if plane_id == 0:
            data = {
                'header': 'Установить позывной',
                'grey_btn': 'Закрыть',
                'response': 'Нельзя изменить позывной этому самолёту',
            }
            return JResponse(data)

        #  выбор другого самолёта
        if Plane.objects.filter(player=player, pk=plane_id).exists():
            plane = Plane.objects.get(pk=plane_id)

            if nickname == plane.nickname:
                data = {
                    'response': 'Позывной не изменился',
                    'header': 'Установить позывной',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

            plane.nickname = nickname[:25]
            plane.save()

            data = {
                'response': 'ok',
            }
            return JResponse(data)

        else:
            return {
                'header': 'Установить позывной',
                'grey_btn': 'Закрыть',
                'response': 'Указанный самолёт вам не принадлежит',
            }

    # если страницу только грузят
    else:
        data = {
            'response': _('Ошибка метода'),
            'header': 'Установить позывной',
            'grey_btn': _('Закрыть'),
        }
        return JResponse(data)
