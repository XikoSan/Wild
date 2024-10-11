import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import pgettext
from time import gmtime
from time import strftime
from player.decorators.player import check_player
from player.player import Player
from region.models.region import Region
from region.views.distance_counting import distance_counting
from region.views.time_in_flight import time_in_flight


@check_player
def region_info(request, id):
    if request.method == "GET":

        player = Player.get_instance(account=request.user)

        if Region.objects.filter(on_map_id=id).exists():

            cost = round(distance_counting(player.region, Region.objects.get(on_map_id=id)))

            groups = list(player.account.groups.all().values_list('name', flat=True))
            page = 'region/region_info.html'
            if 'redesign' not in groups:
                page = 'region/redesign/region_info.html'

            return render(request, page, {
                'player': player,
                'region': Region.objects.get(on_map_id=id),
                'duration': round(time_in_flight(player, Region.objects.get(on_map_id=id)) / 60, 1),
                'time': strftime("%M:%S", gmtime(time_in_flight(player, Region.objects.get(on_map_id=id)))),
                'cost': cost
            })

        else:
            data = {
                'response': pgettext('region_info', 'Такого региона нет'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'header': pgettext('region_info', 'Информация о регионе'),
            }
            return JsonResponse(data)

    else:
        data = {
            'response': pgettext('core', 'Ошибка метода'),
            'grey_btn': pgettext('core', 'Закрыть'),
            'header': pgettext('region_info', 'Информация о регионе'),
        }
        return JsonResponse(data)
