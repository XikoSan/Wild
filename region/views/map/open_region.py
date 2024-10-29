import redis
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from time import gmtime
from time import strftime

from gov.models.residency_request import ResidencyRequest
from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from player.views.get_subclasses import get_subclasses
from region.building.building import Building
from region.models.fossils import Fossils
from region.models.region import Region
from region.views.distance_counting import distance_counting
from region.views.time_in_flight import time_in_flight
from war.models.martial import Martial
from django.utils import timezone


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

        if residency == 'issue' and ResidencyRequest.objects.filter(char=player, region=region,
                                                                    state=region.state).exists():
            res_request = ResidencyRequest.objects.get(char=player, region=region, state=region.state)

    players_count = Player.objects.filter(banned=False, region=region).count()
    residents_count = Player.objects.filter(banned=False, residency=region).count()

    parties_count = Party.objects.filter(region=region, deleted=False).count()

    cost = round(distance_counting(player.region, region))

    fossils = Fossils.objects.filter(region=region).order_by('-good__name_ru')

    terrains = region.terrain.all()

    martial = False
    if Martial.objects.filter(active=True, region=region).exists():
        martial = True

    peace_date = None
    if region.peace_date > timezone.now():
        peace_date = region.peace_date

    return render(request, 'region/redesign/region_view.html', {
        'page_name': region.region_name,
        'player': player,
        'region': region,
        'cost': cost,

        'time': strftime("%M:%S", gmtime(time_in_flight(player, region))),

        'fossils': fossils,
        'terrains': terrains,

        'residency': residency,
        'request': res_request,

        'players_count': players_count,
        'residents_count': residents_count,
        'parties_count': parties_count,

        'building_classes': get_subclasses(Building),

        'martial': martial,
        'peace_date': peace_date,

        # 'wars_cnt': wars_cnt,
    })
