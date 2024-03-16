import datetime
import json
import math
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _
from django_celery_beat.models import ClockedSchedule, PeriodicTask

from factory.models.auto_produce import AutoProduce
from player.decorators.player import check_player
from player.logs.auto_mining import AutoMining
from player.logs.cash_log import CashLog
from player.player import Player
from region.building.hospital import Hospital
from region.models.map_shape import MapShape
from region.models.region import Region
from region.views.distance_counting import distance_counting
from region.views.lists.get_regions_online import get_region_online
from region.views.time_in_flight import time_in_flight
from wild_politics.settings import JResponse
from region.models.neighbours import Neighbours
from player.views.timers import interval_in_seconds
from region.models.fossils import Fossils
from region.building.infrastructure import Infrastructure


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
        med_index_dict = {}
        infr_index_dict = {}
        oil_type_dict = {}

        ore_type_dict = {}
        ore_has_dict = {}

        min_online = 0
        max_online = 0

        shapes = MapShape.objects.all()

        hospitals = Hospital.objects.all()

        infrastructure = Infrastructure.objects.all()

        neighbours = Neighbours.objects.all()

        fossils = Fossils.objects.all()

        for region in regions:
            shapes_dict[region.pk] = shapes.get(region=region)

            # онлайн регионов
            dummy, online_dict[region.pk], dummy2 = get_region_online(region)

            if online_dict[region.pk] > max_online:
                max_online = online_dict[region.pk]

            if online_dict[region.pk] < min_online:
                min_online = online_dict[region.pk]

            # медицина регионов
            if hospitals.filter(region=region).exists():
                med_index_dict[region.pk] = hospitals.get(region=region).top
            else:
                med_index_dict[region.pk] = 1

            # инфраструктура регионов
            if infrastructure.filter(region=region).exists():
                infr_index_dict[region.pk] = infrastructure.get(region=region).top
            else:
                infr_index_dict[region.pk] = 1

            # типы нефти
            if region.oil_mark.pk not in oil_type_dict.keys():
                oil_type_dict[region.oil_mark.pk] = region.oil_mark.name

            # типы руды
            max_fossil = 0
            max_fossil_id = None

            for fossil in fossils.filter(region=region):

                if fossil.good.pk not in ore_type_dict.keys():
                    ore_type_dict[fossil.good.pk] = fossil.good.name

                if fossil.percent > max_fossil:
                    max_fossil_id = fossil.good.pk
                    max_fossil = fossil.percent

            ore_has_dict[region.pk] = max_fossil_id


        duration = 0
        estimate = 0
        if player.destination:
            duration = math.floor(time_in_flight(player, player.destination))
            estimate = duration - math.floor(interval_in_seconds(object=player.task.clocked, start_fname=None, end_fname='clocked_time', delay_in_sec=None))

        admin = None
        admin_duration = 0
        admin_estimate = 0

        if not player.pk == 1:
            admin = Player.get_instance(pk=1)

            if admin.destination:
                admin_duration = math.floor(time_in_flight(admin, admin.destination))
                admin_estimate = admin_duration - math.floor(interval_in_seconds(object=admin.task.clocked, start_fname=None, end_fname='clocked_time', delay_in_sec=None))

        groups = list(player.account.groups.all().values_list('name', flat=True))
        page = 'region/map.html'
        if 'redesign' not in groups:
            page = 'region/redesign/map.html'

        response = render(request, page, {
            'page_name': _('Карта'),

            'player': player,
            'regions': regions,
            'shapes_dict': shapes_dict,

            'duration': duration,
            'estimate': estimate,

            'admin': admin,
            'admin_duration': admin_duration,
            'admin_estimate': admin_estimate,

            'online_dict': online_dict,
            'min_online': min_online,
            'max_online': max_online,
            'neighbours': neighbours,
            'oil_type_dict': oil_type_dict,

            'ore_type_dict': ore_type_dict,
            'ore_has_dict': ore_has_dict,

            # словарь медки
            'med_index_dict': med_index_dict,
            # словарь инфры
            'infr_index_dict': infr_index_dict,
        })

        # if player_settings:
        #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
        return response
