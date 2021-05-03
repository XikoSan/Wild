from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from player.decorators.player import check_player
from player.player import Player
from region.views.distance_counting import distance_counting
from storage.models.cash_lock import CashLock
from storage.models.good_lock import GoodLock
from storage.models.storage import Storage
from storage.models.trade_offer import TradeOffer


@login_required(login_url='/')
@check_player
# получить торговыые предложения
def get_offers(request):
    if request.method == "POST":

        player = Player.objects.get(account=request.user)
        kwargs = {}

        # узнаём действие, которое игрок хочет совершить
        action = request.POST.get('action')

        if not (action == 'sell' or action == 'buy'):
            data = {
                'response': 'Некорректное действие',
                'header': 'Ошибка получения офферов',
                'grey_btn': 'Закрыть',
            }
            return JsonResponse(data)
        else:
            kwargs['type'] = action

        # # берем торговые предложения только из указанных регионов
        # range = request.POST.get('range')
        #
        # if not (range in ['all', 'state', 'range', 'this']):
        #     data = {
        #         'response': 'Некорректная область',
        #     }
        #     return JsonResponse(data)

        # узнаём владельцев офферов
        owner = request.POST.get('owner')

        if not (owner in ['all', 'mine', 'party']):
            data = {
                'response': 'Некорректный владелец',
                'header': 'Ошибка получения офферов',
                'grey_btn': 'Закрыть',
            }
            return JsonResponse(data)
        else:
            if owner == 'mine':
                kwargs['owner_storage__owner__pk'] = player.pk
            elif owner == 'party':
                # если у игрока есть партия
                if player.party:
                    # получаем всех однопартийцев
                    kwargs['owner_storage__owner__pk__in'] = Player.objects.filter(party=player.party).values('pk')
                else:
                    # иначе - личные
                    kwargs['owner_storage__owner__pk'] = player.pk

        # узнаём конкретный товар
        good = request.POST.get('good')

        all_goods = [good_tuple[0] for good_tuple in TradeOffer.goodsChoises]
        if good in all_goods:
            kwargs['good'] = good
        else:
            # узнаём группы товаров
            groups = request.POST.get('groups').split(',')

            goods_list = []
            for group in groups:
                if group in Storage.types.keys():
                    for good in getattr(Storage, group).keys():
                        goods_list.append(good)

            if goods_list:
                kwargs['good__in'] = goods_list

        offers = TradeOffer.actual.filter(**kwargs)

        offers_list = []

        for offer in offers:
            offer_dict = {}
            offer_dict['good'] = offer.get_good_display()
            offer_dict['owner'] = offer.owner_storage.owner.nickname
            offer_dict['region'] = offer.owner_storage.region.region_name
            offer_dict['count'] = offer.count
            offer_dict['price'] = offer.price
            offer_dict['delivery'] = 0
            offer_dict['sum'] = 0
            offers_list.append(offer_dict)

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
