import datetime
import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _
from django_celery_beat.models import ClockedSchedule, PeriodicTask

from player.decorators.player import check_player
from player.logs.auto_mining import AutoMining
from factory.models.auto_produce import AutoProduce
from player.logs.cash_log import CashLog
from player.player import Player
from region.models.region import Region
from region.views.distance_counting import distance_counting
from region.views.time_in_flight import time_in_flight
from wild_politics.settings import JResponse
from region.models.map_shape import MapShape
from region.views.lists.get_regions_online import get_region_online



# главная страница
@login_required(login_url='/')
@check_player
@transaction.atomic
def map(request):
    player = Player.get_instance(account=request.user)

    regions = Region.objects.all()

    # форма по перелету игрока в другой регион
    if request.method == "POST":

        destination = request.POST.get('region')

        if Region.objects.filter(pk=destination).exists():
            destination = Region.objects.get(pk=destination)

        else:
            data = {
                'header': 'Ошибка полёта',
                'grey_btn': 'Закрыть',
                'response': 'Указанный регион не существует',
            }
            return JResponse(data)

        cost = round(distance_counting(player.region, destination))

        if player.cash >= cost:
            if not player.destination:

                if AutoMining.objects.filter(player=player).exists():
                    AutoMining.objects.filter(player=player).delete()

                # if AutoProduce.objects.filter(player=player).exists():
                #     AutoProduce.objects.filter(player=player).delete()

                player.destination = destination
                player.cash -= cost
                player.save()

                CashLog.create(player=player, cash=0 - cost, activity_txt='flyin')

                duration = time_in_flight(player, player.destination)
                # move_to_another_region.apply_async((player.id,), countdown=duration)

                start_time = timezone.now() + datetime.timedelta(seconds=duration)
                clock, created = ClockedSchedule.objects.get_or_create(clocked_time=start_time)

                player.task = PeriodicTask.objects.create(
                    name=str(player.pk) + ' fly ' + str(player.destination.pk),
                    task='move_to_another_region',
                    clocked=clock,
                    one_off=True,
                    args=json.dumps([player.pk]),
                    start_time=timezone.now()
                )
                player.save()

                data = {
                    'response': 'ok',
                }
                return JResponse(data)

            else:
                data = {
                    'header': 'Ошибка полёта',
                    'grey_btn': 'Закрыть',
                    'response': 'Вы уже в полёте',
                }
                return JResponse(data)

        else:
            data = {
                'header': 'Ошибка полёта',
                'grey_btn': 'Закрыть',
                'response': 'Недостаточно денег. В наличии: $' + str(player.cash) + ' , требуется: $' + str(cost),
            }
            return JResponse(data)

    else:
        shapes_dict = {}
        online_dict = {}
        min_online = 0
        max_online = 0
        shapes = MapShape.objects.all()

        for region in regions:
            shapes_dict[region.pk] = shapes.get(region=region)
            dummy, online_dict[region.pk], dummy2 = get_region_online(region)

            if online_dict[region.pk] > max_online:
                max_online = online_dict[region.pk]

            if online_dict[region.pk] < min_online:
                min_online = online_dict[region.pk]


        groups = list(player.account.groups.all().values_list('name', flat=True))
        page = 'region/map.html'
        if 'redesign' not in groups:
            page = 'region/redesign/map.html'

        response = render(request, page, {
            'page_name': _('Карта'),

            'player': player,
            'regions': regions,
            'shapes_dict': shapes_dict,

            'online_dict': online_dict,
            'min_online': min_online,
            'max_online': max_online,
        })

        # if player_settings:
        #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
        return response
