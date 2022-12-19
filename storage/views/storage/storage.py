from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from storage.models.storage import Storage
from storage.templatetags.check_up_limit import check_up_limit
from war.models.wars.war import War
from player.views.get_subclasses import get_subclasses


# главная страница
@login_required(login_url='/')
@check_player
def storage(request):
    player = Player.get_instance(account=request.user)
    storage = None

    war_there = False

    # если склад есть
    if Storage.actual.filter(owner=player, region=player.region).exists():
        storage = Storage.actual.get(owner=player, region=player.region)

    # для переноса склада - должен быть один
    single_storage = None
    if Storage.actual.filter(owner=player).count() == 1:
        single_storage = Storage.actual.get(owner=player)

        # если идет война за этот регион
        war_classes = get_subclasses(War)
        for war_cl in war_classes:
            # если есть войны за этот рег
            if war_cl.objects.filter(running=True, def_region=single_storage.region).exists():
                war_there = True
                break

    # наличие алюминия и стали на текущем складе - для прокачки
    can_upgrade = False

    limit_upgrade = True

    if storage:
        if storage.aluminium >= 500 and storage.steel >= 500:
            can_upgrade = True

        if storage.level < 5:
            limit_upgrade = False

    # ------------
    large_limit = 5
    medium_limit = 6
    small_limit = 5

    # отправляем в форму
    response = render(request, 'storage/redesign/storage.html', {
        'page_name': pgettext('storage', 'Склад'),

        'player': player,
        'storage': storage,

        'war_there': war_there,

        'single_storage': single_storage,

        'can_upgrade': can_upgrade,
        'limit_upgrade': limit_upgrade,

        'large_limit': large_limit,
        'medium_limit': medium_limit,
        'small_limit': small_limit,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
