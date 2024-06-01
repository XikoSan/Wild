from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from ava_border.models.ava_border_ownership import AvaBorderOwnership


@login_required(login_url='/')
@check_player
# открытие страницы выбора самолётов
def border_select(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    borders = None
    used = None

    if AvaBorderOwnership.objects.filter(owner=player).exists():
        borders = AvaBorderOwnership.objects.filter(owner=player)

        if borders.filter(in_use=True).exists():
            used = borders.get(in_use=True)


    return render(request, 'player/redesign/customization/border_select.html', {
                                                            'page_name': _('Выбор рамки'),
                                                            'player': player,
                                                            'borders': borders,
                                                            'used': used,
                                                           })
