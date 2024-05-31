from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from region.models.plane import Plane


@login_required(login_url='/')
@check_player
# открытие страницы выбора самолётов
def plane_select(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    planes = None
    used = None

    if Plane.objects.filter(player=player).exists():
        planes = Plane.objects.filter(player=player).order_by('plane')

        if planes.filter(in_use=True).exists():
            used = planes.get(in_use=True)


    return render(request, 'player/redesign/customization/plane_select.html', {
                                                            'page_name': _('Выбор авиации'),
                                                            'player': player,
                                                            'planes': planes,
                                                            'used': used,

                                                            'golds': Plane.gold_colors,
                                                           })
