from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
import math
from player.decorators.player import check_player
from player.player import Player
from region.views.distance_counting import distance_counting
from storage.views.storage.get_transfer_price import get_transfer_price
from storage.models.cash_lock import CashLock
from storage.models.good_lock import GoodLock
from storage.models.storage import Storage
from storage.models.trade_offer import TradeOffer
from player.logs.print_log import log

@login_required(login_url='/')
@check_player
# получить торговыые предложения
def get_offers(request):
    if request.method == "POST":

        player = Player.objects.get(account=request.user)
        storages = {}

        if Storage.actual.filter(owner=player).exists():
            storages = Storage.actual.filter(owner=player)

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
            offer_dict = {'good': offer.get_good_display(),
                          'good_name': offer.good,
                          'owner': offer.owner_storage.owner.nickname,
                          'region': offer.owner_storage.region.region_name,
                          'count': offer.count,
                          'price': offer.price
                          }

            delivery_dict = {}

            for storage in storages:
                trans_mul = {storage.pk: {}}
                trans_mul[storage.pk][offer.owner_storage.pk] = math.ceil(
                    distance_counting(storage.region, offer.owner_storage.region) / 100)

                offer_value = {}
                offer_value[str(offer.owner_storage.pk)] = {}
                offer_value[str(offer.owner_storage.pk)][offer.good] = offer.count

                delivery_dict[storage.pk] = {}
                delivery_dict[storage.pk]['name'] = storage.region.region_name
                if len(delivery_dict) == 1:
                    delivery_dict[storage.pk]['single'] = trans_mul[storage.pk][offer.owner_storage.pk]
                delivery_dict[storage.pk]['delivery'], prices = get_transfer_price(trans_mul, int(storage.pk), offer_value)

            offer_dict['delivery'] = delivery_dict

            delivery_val = 0
            for key, value in offer_dict['delivery'].items():
                if 'single' in value:
                    delivery_val = value['delivery']
                    break

            if offer.type == 'sell':
                offer_dict['sum'] = (offer.price * offer.count) + delivery_val
            else:
                offer_dict['sum'] = (offer.price * offer.count) - delivery_val

            offers_list.append(offer_dict)

            offer_dict['type'] = offer.type
            if offer.type == 'sell':
                offer_dict['type_action'] = 'Купить'
            else:
                offer_dict['type_action'] = 'Продать'

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
