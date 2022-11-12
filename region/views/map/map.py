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
from player.logs.cash_log import CashLog
from player.player import Player
from region.region import Region
from region.views.distance_counting import distance_counting
from region.views.time_in_flight import time_in_flight
from wild_politics.settings import JResponse


# главная страница
@login_required(login_url='/')
@check_player
@transaction.atomic
def map(request):
    player = Player.get_instance(account=request.user)

    regions = Region.with_off.all()

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

        response = render(request, 'region/map.html', {
            'page_name': _('Карта'),

            'player': player,
            'regions': regions,
        })

        # if player_settings:
        #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
        return response
