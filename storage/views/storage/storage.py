from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from django.utils import timezone
from storage.models.storage import Storage
from storage.templatetags.check_up_limit import check_up_limit
from war.models.wars.war import War
from player.views.get_subclasses import get_subclasses
from storage.models.stock import Stock
from storage.models.good import Good
from player.lootbox.lootbox import Lootbox


# главная страница
@login_required(login_url='/')
@check_player
def storage(request):
    player = Player.get_instance(account=request.user)

    premium = False
    if player.premium > timezone.now():
        premium = True

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
        if Good.objects.filter(name='Алюминий').exists()\
                and Good.objects.filter(name='Сталь').exists():

            alu = Good.objects.get(name='Алюминий')
            steel = Good.objects.get(name='Сталь')

            if Stock.objects.filter(storage=storage, good=alu, stock__gte=500).exists()\
                    and Stock.objects.filter(storage=storage, good=steel, stock__gte=500).exists():
                can_upgrade = True

            if storage.level < 5:
                limit_upgrade = False

    # ------------
    large_limit = 5
    medium_limit = 6
    small_limit = 5

    lootbox_count = 0
    if Lootbox.objects.filter(player=player).exists():
        lootbox_count = Lootbox.objects.get(player=player).stock

    # отправляем в форму
    response = render(request, 'storage/redesign/storage.html', {
        'page_name': pgettext('storage', 'Склад'),

        'player': player,
        'premium': premium,
        'storage': storage,

        'war_there': war_there,

        'single_storage': single_storage,

        'can_upgrade': can_upgrade,
        'limit_upgrade': limit_upgrade,

        'large_limit': large_limit,
        'medium_limit': medium_limit,
        'small_limit': small_limit,

        'lootbox_count': lootbox_count,

    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
