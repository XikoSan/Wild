from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from region.models.plane import Plane
from storage.models.lootbox_prize import LootboxPrize


@login_required(login_url='/')
@check_player
# открытие страницы выбора самолётов
def plane_select(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    if LootboxPrize.objects.filter(player=player, deleted=False).exists():
        for prize in LootboxPrize.objects.filter(player=player, deleted=False):
            if not Plane.objects.filter(player=player, plane=prize.plane, color=prize.color).exists():
                plane = Plane(player=player, plane=prize.plane, color=prize.color)
                plane.save()

        LootboxPrize.objects.filter(player=player, deleted=False).update(deleted=True)

    used = None

    lists = {
        'common_list': [],
        'rare_list': [],
        'epic_list': [],
    }

    if Plane.objects.filter(player=player).exists():
        planes = Plane.objects.filter(player=player).order_by('plane')

        if planes.filter(in_use=True).exists():
            used = planes.get(in_use=True)

        rare_colors = Plane.rare_colors
        epic_colors = Plane.gold_colors

        for plane in planes:

            if plane.color in epic_colors:
                lists['epic_list'].append(plane)

            elif plane.color in rare_colors:
                lists['rare_list'].append(plane)

            else:
                lists['common_list'].append(plane)

    return render(request, 'player/redesign/customization/plane_select.html', {
                                                            'page_name': pgettext('plane_select', 'Выбор авиации'),
                                                            'player': player,

                                                            'rarity_list': ['epic', 'rare', 'common' ],
                                                            'lists': lists,
                                                            'used': used,

                                                            'golds': Plane.gold_colors,
                                                           })
