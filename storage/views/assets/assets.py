import math
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from region.views.distance_counting import distance_counting
from storage.models.storage import Storage
from storage.models.transport import Transport
from datetime import datetime
from storage.views.storage.locks.get_storage import get_stocks
from storage.models.good import Good
from storage.models.stock import Stock
from region.building.infrastructure import Infrastructure
from region.views.find_route import find_route


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

    # ненулевые запасы
    stocks = Stock.objects.filter(storage__in=storages, stock__gt=0, good__in=all_goods)

    for storage in storages:
        all_stocks[storage] = {}

        if storage == storages.first():
            for good in all_goods:

                if stocks.filter(storage=storage, good=good).exists():

                    stock = stocks.get(storage=storage, good=good, stock__gt=0)

                    if good.size in all_stocks[storage]:
                        all_stocks[storage][good.size].append(stock)
                    else:
                        all_stocks[storage][good.size] = [stock, ]


        trans_mul[storage.pk] = {}
        for dest in storages:
            if not dest == storage:
                trans_mul[storage.pk][dest.pk] = math.ceil(distance_counting(storage.region, dest.region) / 100)
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
