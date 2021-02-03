from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from region.region import Region
from region.views.distance_counting import distance_counting
from region.views.time_in_flight import time_in_flight


@check_player
def region_info(request, id):
    if request.method == "GET":

        player = Player.objects.get(account=request.user)

        if player.residency == Region.objects.get(on_map_id=id):
            cost = 0
        else:
            cost = round(distance_counting(player.region, Region.objects.get(on_map_id=id)))

        return render(request, 'region/region_info.html', {
            'player': player,
            'region': Region.objects.get(on_map_id=id),
            'duration': round(time_in_flight(player, Region.objects.get(on_map_id=id)) / 60, 1),
            'cost': cost
        })

    else:
        data = {
            'response': _('Некорректный запрос'),
        }
        return JsonResponse(data)
