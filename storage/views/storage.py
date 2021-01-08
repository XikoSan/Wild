from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.decorators.player import check_player
from player.player import Player
from storage.storage import Storage


# главная страница
@login_required(login_url='/')
@check_player
def storage(request):
    player = Player.objects.get(account=request.user)
    storage = None
    # если склад есть
    if Storage.objects.filter(owner=player, region=player.region).exists():
        storage = Storage.objects.get(owner=player, region=player.region)
    # отправляем в форму
    response = render(request, 'storage/storage.html', {
        # 'page_name': _('Overview'),

        'player': player,
        'storage': storage,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
