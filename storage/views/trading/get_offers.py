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
from django.utils.translation import pgettext
from war.models.wars.war import War
from player.views.get_subclasses import get_subclasses
from storage.models.good import Good
from storage.models.stock import Stock
from math import ceil


@login_required(login_url='/')
@check_player
# получить торговыые предложения
def get_offers(request):
    if request.method == "POST":

        player = Player.get_instance(account=request.user)
        storages = {}

        if Storage.actual.filter(owner=player).exists():
            storages = Storage.actual.filter(owner=player)

        kwargs = {}
        ex_kwargs = {}
        dis_args = ['owner_storage', 'price', 'view_type', 'offer_good']

        # узнаём действие, которое игрок хочет совершить
        action = request.POST.get('action')

        if not (action == 'sell' or action == 'buy'):
            data = {
                'header': pgettext('w_trading', 'Получение офферов'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading_new', 'Некорректное действие'),
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
                'header': pgettext('w_trading', 'Получение офферов'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'Некорректный владелец'),
            }
            return JsonResponse(data)
        else:
            if owner == 'mine':
                kwargs['owner_storage__owner__pk'] = player.pk
                dis_args = []
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

        try:
            good = int(good)

        except ValueError:
            pass
            # if owner != 'mine':
            #     data = {
            #         'header': pgettext('w_trading', 'Получение офферов'),
            #         'grey_btn': pgettext('mining', 'Закрыть'),
            #         'response': pgettext('w_trading_new', 'ID товара должен быть целым числом'),
            #     }
            #     return JsonResponse(data)

        if good != 'null' and (Good.objects.filter(pk=good).exists() or good == -1):
            if good == -1:
                kwargs['wild_pass'] = True
            else:
                good_obj = Good.objects.get(pk=good)
                kwargs['offer_good'] = good_obj

        else:
            # if owner != 'mine':
            #     data = {
            #         'header': pgettext('w_trading', 'Получение офферов'),
            #         'grey_btn': pgettext('mining', 'Закрыть'),
            #         'response': pgettext('w_trading', 'Укажите товар'),
            #     }
            #     return JsonResponse(data)

            # узнаём группы товаров
            groups = request.POST.get('groups').split(',')

            types_list = []
            for type in Good.typeChoices:
                types_list.append(type[0])

            goods_list = []
            for group in groups:
                if group in types_list:
                    for good_obj in Good.objects.filter(type=group):
                        goods_list.append(good_obj)

                elif group == 'premium':
                    kwargs['wild_pass'] = True

            if goods_list:
                kwargs['offer_good__in'] = goods_list

        # # отсекаем Склады, в регионах которых идёт война, если выбирают не личные предложения
        # if owner != 'mine':
        #     dest_regions = []
        #     war_classes = get_subclasses(War)
        #     for war_cl in war_classes:
        #         # если есть войны за этот рег
        #         if war_cl.objects.filter(running=True).exists():
        #             # айдишники всех целевых регов
        #             tmp_war_list = war_cl.objects.filter(running=True).values_list('def_region__pk')
        #             for dest_pk in tmp_war_list:
        #                 if not dest_pk[0] in dest_regions:
        #                     dest_regions.append(dest_pk[0])
        #     ex_kwargs['owner_storage__region__pk__in'] = dest_regions

        offers = TradeOffer.actual.filter(**kwargs).exclude(**ex_kwargs).order_by('price').distinct(*dis_args)

        offers_list = []

        for offer in offers:
            offer_dict = {'owner': offer.owner_storage.owner.nickname,
                          'region': pgettext('regions_list', offer.owner_storage.region.region_name),
                          'region_img': offer.owner_storage.region.on_map_id,
                          'count': offer.count,
                          'price': offer.price
                          }

            if offer.wild_pass:
                offer_dict['good'] = -1
                offer_dict['good_name'] = 'Wild Pass'

            else:
                offer_dict['good'] = offer.offer_good.pk
                offer_dict['good_name'] = offer.offer_good.name

            if offer.owner_storage.owner.pk == player.pk:
                offer_dict['own_offer'] = True
            else:
                offer_dict['own_offer'] = False

            if offer.owner_storage.owner.image:
                offer_dict['owner_img'] = offer.owner_storage.owner.image.url
            else:
                offer_dict['owner_img'] = 'None'

            delivery_dict = {}

            for storage in storages:
                if offer.wild_pass:
                    delivery_dict[storage.pk] = {}
                    delivery_dict[storage.pk]['delivery'] = 0
                    delivery_dict[storage.pk]['single'] = 0
                    continue

                trans_mul = {storage.pk: {}}
                trans_mul[storage.pk][offer.owner_storage.pk] = math.ceil(
                    distance_counting(storage.region, offer.owner_storage.region) / 100)

                # offer_value = {}
                # offer_value[str(offer.owner_storage.pk)] = {}
                # offer_value[str(offer.owner_storage.pk)][offer.offer_good.pk] = offer.count

                delivery_dict[storage.pk] = {}
                delivery_dict[storage.pk]['name'] = storage.region.region_name
                delivery_dict[storage.pk]['img'] = storage.region.on_map_id
                if len(delivery_dict) == 1:
                    delivery_dict[storage.pk]['default'] = True
                delivery_dict[storage.pk]['single'] = trans_mul[storage.pk][offer.owner_storage.pk]

                # delivery_dict[storage.pk]['delivery'], prices = get_transfer_price(trans_mul, int(storage.pk), offer_value)
                delivery_dict[storage.pk]['delivery'] = ceil(int(offer.count) * offer.offer_good.volume) * trans_mul[storage.pk][offer.owner_storage.pk]

            offer_dict['delivery'] = delivery_dict

            delivery_val = 0
            for key, value in offer_dict['delivery'].items():
                if 'default' in value:
                    delivery_val = value['delivery']
                    break

            if offer.type == 'sell':
                offer_dict['sum'] = (offer.price * offer.count) + delivery_val
            else:
                offer_dict['sum'] = (offer.price * offer.count) - delivery_val

            offers_list.append(offer_dict)

            offer_dict['type'] = offer.type

            if offer.owner_storage.owner == player:
                offer_dict['my_offer'] = True
                offer_dict['type_action'] = pgettext('w_trading', 'Отменить')
            else:
                offer_dict['my_offer'] = False
                if offer.type == 'sell':
                    offer_dict['type_action'] = pgettext('w_trading', 'Купить')
                else:
                    offer_dict['type_action'] = pgettext('w_trading', 'Продать')

            offer_dict['id'] = offer.pk

        data = {
            'response': 'ok',
            'offers_list': offers_list,
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'header': pgettext('w_trading', 'Получение офферов'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': pgettext('mining', 'Ошибка метода'),
        }
        return JsonResponse(data)
