import pytz
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min, Sum
from django.http import JsonResponse
from django.utils import timezone

from player.decorators.player import check_player
from player.player import Player
from storage.models.auction.auction import BuyAuction
from storage.models.auction.auction_bet import AuctionBet
from storage.models.auction.auction_lot import AuctionLot
from storage.models.storage import Storage
from storage.models.good import Good


@login_required(login_url='/')
@check_player
# получить список аукционов
def get_auctions(request):
    if request.method == "POST":

        player = Player.get_instance(account=request.user)

        kwargs = {}

        # узнаём конкретный товар
        good = request.POST.get('good')

        all_goods = [good_tuple[0] for good_tuple in Storage.get_choises()]
        if good in all_goods:
            kwargs['good'] = good
        else:
            # узнаём группы товаров
            groups = request.POST.get('groups').split(',')

            kwargs['good__in'] = Good.objects.only("player").filter(type__in=groups)

        from player.logs.print_log import log
        log(kwargs)
        offers = BuyAuction.actual.filter(**kwargs)

        offers_pk_list = []
        for offer in offers:
            offers_pk_list.append(offer.pk)

        auction_lots = AuctionLot.actual.filter(auction__in=offers_pk_list)

        offers_list = []
        for offer in offers:

            offer_lots = auction_lots.filter(auction=offer)

            offer_bets_all = AuctionBet.actual.filter(auction_lot__in=offer_lots)

            no_bet_exists = True
            for lot in offer_lots:
                no_bet_exists = offer_bets_all.filter(auction_lot=lot).exists()
                if not no_bet_exists:
                    break

            offer_bets = AuctionBet.actual.filter(auction_lot__in=offer_lots).aggregate(Min('price'), Max('price'))

            price_min = offer_bets['price__min']
            price_max = offer_bets['price__max']

            if not price_min\
                    or not no_bet_exists:
                price_min = offer_lots[0].start_price

            if not price_max:
                price_max = offer_lots[0].start_price

            offer_time = timezone.localtime(offer.create_date, pytz.timezone(player.time_zone))

            offer_dict = {'id': offer.pk,
                          'good': offer.good.name,
                          'good_name': offer.good.pk,
                          'time': offer_time.strftime('%d.%m %H:%M'),
                          'owner': offer.treasury_lock.lock_treasury.state.title,
                          'owner_img': offer.treasury_lock.lock_treasury.state.image.url,
                          'count': offer_lots.aggregate(Sum('count'))['count__sum'],
                          'price': offer_lots[0].start_price,
                          'lot_cnt': offer_lots.count(),
                          'price_min': price_min,
                          'price_max': price_max
                          }

            offers_list.append(offer_dict)

            offer_dict['id'] = offer.pk

        data = {
            'response': 'ok',
            'offers_list': offers_list,
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': 'Ты уверен что тебе сюда, путник?',
            'header': 'Ошибка получения офферов',
            'grey_btn': 'Закрыть',
        }
        return JsonResponse(data)
