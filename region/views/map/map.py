from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist

from player.decorators.player import check_player
from player.player import Player

from region.views.time_in_flight import time_in_flight
from region.region import Region
from region.tasks import move_to_another_region

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

        player.destination = destination
        player.save()
        duration = time_in_flight(player, player.destination)
        # move_to_another_region.s(player.id).apply_async(countdown=duration)
        move_to_another_region.apply_async((player.id,), countdown=duration)

    
    response = render(request, 'region/map.html', {
        'page_name': _('Карта'),

        'player': player,
        'regions': regions,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
