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
# выбор самолётов
def choose_plane(request):
    if request.method == "POST":
        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        try:
            plane_id = int(request.POST.get('plane_id'))

        except ValueError:
            return {
                'header': 'Выбор авиации',
                'grey_btn': 'Закрыть',
                'response': 'ID техники должен быть целым числом',
            }

        # сбросить самолет до дефолтного
        if plane_id == 0:
            Plane.objects.filter(player=player).update(in_use=False)

            data = {
                'response': 'ok',
            }
            return JResponse(data)

        #  выбор другого самолёта
        if Plane.objects.filter(player=player, pk=plane_id).exists():
            plane = Plane.objects.get(pk=plane_id)
            plane.in_use = True
            plane.save()

            data = {
                'response': 'ok',
            }
            return JResponse(data)

        else:
            return {
                'header': 'Выбор авиации',
                'grey_btn': 'Закрыть',
                'response': 'Указанный самолёт вам не принадлежит',
            }

    # если страницу только грузят
    else:
        data = {
            'response': _('Ошибка метода'),
            'header': 'Выбор авиации',
            'grey_btn': _('Закрыть'),
        }
        return JResponse(data)
