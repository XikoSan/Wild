from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils.translation import gettext_lazy, pgettext_lazy

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
                'response': pgettext('set_plane_nick', 'Позывной не может быть пустым'),
                'header': pgettext('set_plane_nick', 'Установить позывной'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        try:
            plane_id = int(request.POST.get('plane_id'))

        except ValueError:
            data = {
                'header': pgettext('set_plane_nick', 'Установить позывной'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('set_plane_nick', 'ID техники должен быть целым числом'),
            }
            return JResponse(data)

        # дефолтного
        if plane_id == 0:
            data = {
                'header': pgettext('set_plane_nick', 'Установить позывной'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('set_plane_nick', 'Нельзя изменить позывной этому самолёту'),
            }
            return JResponse(data)

        #  выбор другого самолёта
        if Plane.objects.filter(player=player, pk=plane_id).exists():
            plane = Plane.objects.get(pk=plane_id)

            if nickname == plane.nickname:
                data = {
                    'response': pgettext('set_plane_nick', 'Позывной не изменился'),
                    'header': pgettext('set_plane_nick', 'Установить позывной'),
                    'grey_btn': pgettext('core', 'Закрыть'),
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
                'header': pgettext('set_plane_nick', 'Установить позывной'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('set_plane_nick', 'Указанный самолёт вам не принадлежит'),
            }

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка метода'),
            'header': pgettext('set_plane_nick', 'Установить позывной'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
