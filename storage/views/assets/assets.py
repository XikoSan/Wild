import math
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from player.views.multiple_sum import multiple_sum
from region.building.infrastructure import Infrastructure
from region.views.distance_counting import distance_counting
from region.views.find_route import find_route
from storage.models.good import Good
from storage.models.stock import Stock
from storage.models.storage import Storage
from storage.models.transport import Transport
from storage.views.storage.locks.get_storage import get_stocks


# главная страница
@login_required(login_url='/')
@check_player
def assets(request):
    player = Player.get_instance(account=request.user)
    # словарь склад - словарь стоимости до других регионов со складами:
    # москва:
    # - архангельск = 15
    # - питер       = 8
    # - моск. обл.  = 1
    trans_mul = {}

    infr_mul = {}

    goods_dict = {}
    cap_dict = {}

    size_dict = {}
    for size in Good.sizeChoices:
        size_dict[size[0]] = size[1]

    all_goods = Good.objects.all()

    # получаем все склады
    storages = Storage.actual.filter(owner=player)
    # запасы по всем складам
    all_stocks = {}

    first_storage = None

    # если в регионе нахождения игрока есть склад
    if storages.filter(region=player.region).exists():
        first_storage = storages.get(region=player.region)

    # если в регионе прописки игрока есть склад
    elif storages.filter(region=player.residency).exists():
        first_storage = storages.get(region=player.residency)

    # иначе - берем первый попавшийся
    else:
        first_storage = storages.first()

    # ненулевые запасы
    stocks = Stock.objects.filter(storage=first_storage, stock__gt=0, good__in=all_goods)

    all_stocks[first_storage] = {}
    for good in all_goods:

        if stocks.filter(storage=first_storage, good=good).exists():

            stock = stocks.get(storage=first_storage, good=good, stock__gt=0)

            if good.size in all_stocks[first_storage]:
                all_stocks[first_storage][good.size].append(stock)
            else:
                all_stocks[first_storage][good.size] = [stock, ]

    # считаем расстояния между ними
    for i, storage in enumerate(storages):

        trans_mul[storage.pk] = {}
        for dest in storages:
            if not dest == storage:
                trans_mul[storage.pk][dest.pk] = multiple_sum(
                    math.ceil(distance_counting(storage.region, dest.region) / 100))
                # path, trans_mul[storage.pk][dest.pk] = find_route(storage.region, dest.region)

        # узнаем множитель Инфраструктуры для этого региона
        infr_mul[storage.pk] = Infrastructure.indexes[Infrastructure.get_stat(storage.region)[0]['top']]

    groups = list(player.account.groups.all().values_list('name', flat=True))
    page = 'storage/assets.html'
    if 'redesign' not in groups:
        page = 'storage/redesign/assets.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('assets', 'Активы'),

        'player': player,
        'first_storage': first_storage,
        'storages': storages,

        'all_stocks': all_stocks,
        'size_dict': size_dict,

        'transport': Transport,
        'storage_cl': Storage,
        'trans_mul': trans_mul,

        'infr_mul': infr_mul,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
