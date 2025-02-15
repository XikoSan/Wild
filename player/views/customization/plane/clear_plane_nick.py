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
# очистить позывной
def clear_plane_nick(request):
    if request.method == "POST":
        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        try:
            plane_id = int(request.POST.get('plane_id'))

        except ValueError:
            data = {
                'header': pgettext('clear_plane_nick', 'Очистить позывной'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('clear_plane_nick', 'ID техники должен быть целым числом'),
            }
            return JResponse(data)

        # сбросить самолет до дефолтного
        if plane_id == 0:
            data = {
                'header': pgettext('clear_plane_nick', 'Очистить позывной'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('clear_plane_nick', 'Нельзя изменить позывной этому самолёту'),
            }
            return JResponse(data)

        #  выбор другого самолёта
        if Plane.objects.filter(player=player, pk=plane_id).exists():
            plane = Plane.objects.get(pk=plane_id)
            plane.nickname = ''
            plane.save()

            data = {
                'response': 'ok',
            }
            return JResponse(data)

        else:
            return {
                'header': pgettext('clear_plane_nick', 'Очистить позывной'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('clear_plane_nick', 'Указанный самолёт вам не принадлежит'),
            }

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка метода'),
            'header': pgettext('clear_plane_nick', 'Очистить позывной'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
