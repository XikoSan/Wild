from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player


# главная страница
@login_required(login_url='/')
@check_player
def mining(request):
    player = Player.objects.get(account=request.user)
    # отправляем в форму
    response = render(request, 'region/mining.html', {
        'page_name': _('Добыча'),

        'player': player,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
