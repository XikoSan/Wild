import datetime
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _
from django_celery_beat.models import ClockedSchedule, PeriodicTask

from player.decorators.player import check_player
from player.player import Player
from region.region import Region
from region.views.time_in_flight import time_in_flight


# главная страница
@login_required(login_url='/')
@check_player
def map(request):
    player = Player.objects.get(account=request.user)

    regions = Region.objects.all()

    # форма по перелету игрока в другой регион
    if request.method == "POST":

        destination = request.POST.get('region')

        try:
            destination = Region.objects.get(on_map_id=destination)
        except Region.DoesNotExist:
            raise Exception("Region is doesn't exist")

        if not player.destination:

            player.destination = destination
            player.save()
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

    response = render(request, 'region/map.html', {
        'page_name': _('Карта'),

        'player': player,
        'regions': regions,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
