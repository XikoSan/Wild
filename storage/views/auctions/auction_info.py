import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.decorators.player import check_player
from player.player import Player
from storage.models.auction.auction import BuyAuction
from storage.models.auction.auction_bet import AuctionBet
from storage.models.auction.auction_lot import AuctionLot
from storage.models.storage import Storage


@login_required(login_url='/')
@check_player
# Открытие страницы аукциона
def auction_info(request, pk):
    if not BuyAuction.actual.filter(pk=pk).exists():
        return redirect('auctions')

    # аукцион скупки
    auction = BuyAuction.actual.get(pk=pk)

    auction.create_date += datetime.timedelta(days=1)

    # Текущий пользователь
    player = Player.objects.get(account=request.user)

    # Его склады
    # собираем из Склада все нужные поля + ресурс
    fields_list = ['pk', 'region__region_name', auction.good]

    storages = Storage.actual.filter(owner=player).values(*fields_list)

    # список лотов
    lots = list(AuctionLot.actual.filter(auction=auction))

    # список ставок
    offer_bets = AuctionBet.actual.filter(auction_lot__in=lots)

    # словарь: лот - ставка, кто поставил
    bets_dict = {}

    for bet in offer_bets:
        bets_dict[bet.auction_lot.pk] = {
            'price': bet.price,
            'owner': bet.good_lock.lock_storage.owner
        }

    return render(request, 'storage/auctions/auction_info.html', {'player': player,
                                                                  'auction': auction,
                                                                  'lots': lots,
                                                                  'bets_dict': bets_dict,
                                                                  'storages': storages
                                                                  })
