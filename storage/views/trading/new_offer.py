from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404

from player.decorators.player import check_player
from player.player import Player
from storage.models.storage import Storage
from storage.models.trade_offer import TradeOffer

@login_required(login_url='/')
@check_player
# новое торговое предложение
def new_offer(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    fields_list = ['pk', 'region__region_name', ]

    # собираем из Склада все поля ресурсов
    for category in Storage.types:
        for good in getattr(Storage, category).keys():
            fields_list.append(good)



    return render(request, 'storage/trading/new_offer.html', {'player': player,
                                                              'storage_cl': Storage,

                                                              'total_offers': Storage.actual.filter(owner=player).count() * 5,
                                                              'free_offers': (Storage.actual.filter(owner=player).count() * 5) - TradeOffer.actual.filter(owner_storage__owner__pk=player.pk).count(),

                                                              'storages': Storage.actual.filter(owner=player).values(*fields_list)
                                                              })
