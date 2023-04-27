from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from storage.models.storage import Storage
from storage.models.transport import Transport
from storage.models.trade_offer import TradeOffer


@login_required(login_url='/')
@check_player
# открытие страницы торговли
def trading(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    storages = None
    if Storage.actual.filter(owner=player).exists():
        storages = Storage.actual.filter(owner=player)

    return render(request, 'storage/redesign/trading/trading.html', {'player': player,
                                                                     'page_name': pgettext('trading', 'Торговля'),
                                                                     'storage_cl': Storage,
                                                                     'transport': Transport,
                                                                     'storages': storages,

                                                                     'total_offers': Storage.actual.filter(
                                                                         owner=player).count() * 5,
                                                                     'free_offers': (Storage.actual.filter(
                                                                         owner=player).count() * 5) - TradeOffer.actual.filter(
                                                                         owner_storage__owner__pk=player.pk).count(),

                                                                     })
