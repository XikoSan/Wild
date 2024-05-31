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

    limit_upgrade = None

    if storage:
        if storage.level >= 5:
            if ( storage.level - 4 ) * 25 > player.knowledge:
                limit_upgrade = ( storage.level - 4 ) * 25

        if not limit_upgrade and\
                Good.objects.filter(name_ru='Алюминий').exists()\
                and Good.objects.filter(name_ru='Сталь').exists():

            alu = Good.objects.get(name_ru='Алюминий')
            steel = Good.objects.get(name_ru='Сталь')

            if Stock.objects.filter(storage=storage, good=alu, stock__gte=500).exists()\
                    and Stock.objects.filter(storage=storage, good=steel, stock__gte=500).exists():
                can_upgrade = True


    # ------------
    lootbox_count = 0
    if Lootbox.objects.filter(player=player).exists():
        lootbox_count = Lootbox.objects.get(player=player).stock

    # ------------

    import datetime

    wildpass_800 = False
    # if datetime.datetime.now() > datetime.datetime(2024, 5, 31, 23, 2):
    if datetime.datetime.now() > datetime.datetime(2024, 6, 1, 0, 0):
        wildpass_800 = True

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

        'lootbox_count': lootbox_count,

        'wildpass_800': wildpass_800,

    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
