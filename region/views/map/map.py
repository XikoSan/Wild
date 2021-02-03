from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

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
    response = render(request, 'region/map.html', {
        'page_name': _('Карта'),

        'player': player,
        'regions': regions,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
