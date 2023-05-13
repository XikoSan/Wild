from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
import redis
from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from player.views.get_subclasses import get_subclasses
from region.building.building import Building
from region.models.region import Region
from region.views.distance_counting import distance_counting
from gov.models.residency_request import ResidencyRequest

@login_required(login_url='/')
@check_player
# Opening page with selected region data
def open_region(request, pk):
    # Получаем объект персонажа, по его ключу
    # Текущий пользователь
    player = Player.get_instance(account=request.user)

    if not Region.objects.filter(pk=pk).exists():
        return redirect('map')

    region = get_object_or_404(Region, pk=pk)

    residency = 'free'
    res_request = None

    if region.state:
        residency = region.state.residency

        if residency == 'issue' and ResidencyRequest.objects.filter(char=player, region=region, state=region.state).exists():
            res_request = ResidencyRequest.objects.get(char=player, region=region, state=region.state)

    players_count = Player.objects.filter(banned=False, region=region).count()
    residents_count = Player.objects.filter(banned=False, residency=region).count()

    parties_count = Party.objects.filter(region=region, deleted=False).count()

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

        'residency': residency,
        'request': res_request,

        'players_count': players_count,
        'residents_count': residents_count,
        'parties_count': parties_count,

        'building_classes': get_subclasses(Building),

        # 'wars_cnt': wars_cnt,
    })
