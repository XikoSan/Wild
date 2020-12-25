from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.decorators.player import check_player
from player.player import Player


# главная страница
@login_required(login_url='/')
@check_player
def party(request):
    player = Player.objects.get(account=request.user)
    # отправляем в форму
    response = render(request, 'party/party.html', {
        # 'page_name': _('Overview'),

        'player': player,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
