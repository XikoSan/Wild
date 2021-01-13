from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from storage.models.storage import Storage


# главная страница
@login_required(login_url='/')
@check_player
def assets(request):
    player = Player.objects.get(account=request.user)

    # получаем все склады
    storages = Storage.objects.filter(owner=player)

    # отправляем в форму
    response = render(request, 'storage/assets.html', {
        'page_name': _('Активы'),

        'player': player,
        'storages': storages,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
