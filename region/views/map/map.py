from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from region.tasks import move_to_another_region

from player.decorators.player import check_player
from player.player import Player
from region.region import Region

# главная страница
@login_required(login_url='/')
@check_player
def map(request):
    player = Player.objects.get(account=request.user)

    regions = Region.objects.all()

    # отправляем в форму
    if request.method == "POST":

        destination = request.POST.get('region')
        duration = request.POST.get('duration')
        # cost = request.POST.get('cost').replace(' ', '')

        destination_object = Region.objects.get(on_map_id=destination)
        player.destination = destination_object
        player.save()
        move_to_another_region.delay(player.id, destination, duration)
        
        return redirect('map')

    
    response = render(request, 'region/map.html', {
        'page_name': _('Карта'),

        'player': player,
        'regions': regions,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
