from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from region.region import Region
from region.views.distance_counting import distance_counting


@login_required(login_url='/')
@check_player
# Opening page with selected region data
def open_region(request, pk):
    # Получаем объект персонажа, по его ключу
    # Текущий пользователь
    player = Player.objects.get(account=request.user)

    if not Region.objects.filter(pk=pk).exists():
        return redirect('map')

    region = get_object_or_404(Region, pk=pk)

    players_count = Player.objects.filter(banned=False, region=region).count()

    parties_count = Party.objects.filter(region=region, deleted=False).count()

    if player.residency == region:
        cost = 0
    else:
        cost = round(distance_counting(player.region, region))

    # # список войн за все время
    # war_types = get_subclasses(War)
    # wars_cnt = 0
    # # -===============================
    # # находим для вывода в Овер ближайшую к завершению войну государства
    # # для каждого типа войн:
    # for type in war_types:
    #     # если есть войны такого типа в регионе
    #     wars_cnt += type.objects.filter(Q(agr_region=region) | Q(def_region=region)).count()

    return render(request, 'region/region_view.html', {
        'page_name': region.region_name,
        'player': player,
        'region': region,
        'cost': cost,

        'players_count': players_count,
        'parties_count': parties_count,

        # 'wars_cnt': wars_cnt,
    })
