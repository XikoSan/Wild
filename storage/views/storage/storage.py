from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from storage.models.storage import Storage


# главная страница
@login_required(login_url='/')
@check_player
def storage(request):
    player = Player.get_instance(account=request.user)
    storage = None

    # если склад есть
    if Storage.actual.filter(owner=player, region=player.region).exists():
        storage = Storage.actual.get(owner=player, region=player.region)

    single_storage = None
    if Storage.actual.filter(owner=player).count() == 1:
        single_storage = Storage.actual.get(owner=player)

    groups = list(player.account.groups.all().values_list('name', flat=True))
    page = 'storage/storage.html'
    if 'redesign' not in groups:
        page = 'storage/redesign/storage.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': _('Склад'),

        'player': player,
        'storage': storage,

        'single_storage': single_storage,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
