from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from storage.models.storage import Storage
from storage.models.transport import Transport
from storage.models.trade_offer import TradeOffer
from storage.models.good import Good
from storage.models.stock import Stock


@login_required(login_url='/')
@check_player
# открытие страницы торговли
def trading(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    storages = None
    if Storage.actual.filter(owner=player).exists():
        storages = Storage.actual.filter(owner=player)

    goods_by_types = {}
    goods = Good.objects.all()

    for good in goods:
        if good.type in goods_by_types:
            goods_by_types[good.type].append(good)
        else:
            goods_by_types[good.type] = [good]

    stocks = []
    if storages:
        stocks = Stock.objects.filter(storage__in=storages)

    total_stocks = {}
    for storage in storages:
        total_stocks[storage.pk] = {}
        for stock in stocks.filter(storage=storage):
            total_stocks[storage.pk][stock.good.pk] = stock.stock

    types_texts = {}
    for type in Good.typeChoices:
        types_texts[type[0]] = type[1]

    return render(request, 'storage/redesign/trading/trading.html', {'player': player,
                                                                     'page_name': pgettext('trading', 'Торговля'),
                                                                     'storage_cl': Storage,

                                                                     'goods': goods,
                                                                     'goods_by_types': goods_by_types,
                                                                     'types_texts': types_texts,

                                                                     'transport': Transport,
                                                                     # все склады
                                                                     'storages': storages,
                                                                     # все запасы
                                                                     'total_stocks': total_stocks,

                                                                     'total_offers': Storage.actual.filter(
                                                                         owner=player).count() * 5,
                                                                     'free_offers': (Storage.actual.filter(
                                                                         owner=player).count() * 5) - TradeOffer.actual.filter(
                                                                         owner_storage__owner__pk=player.pk).count(),

                                                                     })
