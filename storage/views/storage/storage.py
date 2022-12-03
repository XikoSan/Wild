from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from storage.models.storage import Storage
from storage.templatetags.check_up_limit import check_up_limit


# главная страница
@login_required(login_url='/')
@check_player
def storage(request):
    player = Player.get_instance(account=request.user)
    storage = None

    # если склад есть
    if Storage.actual.filter(owner=player, region=player.region).exists():
        storage = Storage.actual.get(owner=player, region=player.region)

    # для переноса склада - должен быть один
    single_storage = None
    if Storage.actual.filter(owner=player).count() == 1:
        single_storage = Storage.actual.get(owner=player)

    # наличие алюминия и стали на текущем складе - для прокачки
    can_upgrade = False

    limit_upgrade = True

    if storage.aluminium >= 500 and storage.steel >= 500:
        can_upgrade = True

    if storage.level < 5:
        limit_upgrade = False

    # ------------
    large_limit = 5
    medium_limit = 6
    small_limit = 5

    # # проверяем, сколько полей можно улучшить
    # for size in Storage.sizes:
    #     limited = 0
    #     for good in Storage.sizes[size]:
    #         # узнаем, поле в лимите или нет
    #         if check_up_limit(storage, good, size):
    #             limited += 1
    #
    #     if size == 'large':
    #         if limited == 5:
    #             large_limit = 1
    #
    #     if size == 'small':
    #         if limited == 5:
    #             small_limit = 1
    #
    #     if size == 'medium':
    #         if limited == 6:
    #             medium_limit = 1

    # отправляем в форму
    response = render(request, 'storage/redesign/storage.html', {
        'page_name': pgettext('storage', 'Склад'),

        'player': player,
        'storage': storage,

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
