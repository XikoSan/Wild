from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from region.views.distance_counting import distance_counting
from storage.models.cash_lock import CashLock
from storage.models.good import Good
from storage.models.good_lock import GoodLock
from storage.models.stock import Stock
from storage.models.storage import Storage
from storage.models.trade_offer import TradeOffer
from storage.views.storage.locks.get_storage import get_stocks


@login_required(login_url='/')
@check_player
@transaction.atomic
# новое торговое предложение
def create_offer(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        # узнаём действие, которое игрок хочет совершить
        action = request.POST.get('action')

        if not (action == 'sell' or action == 'buy'):
            data = {
                'header': pgettext('w_trading_new', 'Создание оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading_new', 'Некорректное действие'),
            }
            return JsonResponse(data)

        # получаем целевой склад
        souce_pk = request.POST.get('storage')

        if not souce_pk.isdigit():
            data = {
                'header': pgettext('w_trading_new', 'Создание оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading_new', 'Склад не указан'),
            }
            return JsonResponse(data)

        # проверяем, есть ли целевой склад среди складов игрока
        storages = Storage.actual.filter(owner=player)
        storages_pk = []

        for storage in storages:
            storages_pk.append(storage.pk)

        if not int(souce_pk) in storages_pk:
            data = {
                'header': pgettext('w_trading_new', 'Создание оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading_new', 'Указанный Склад вам не принадлежит'),
            }
            return JsonResponse(data)

        # проверка на количество уже созданных предложений
        if (storages.count() * 5) - TradeOffer.actual.filter(owner_storage__owner__pk=player.pk).count() <= 0:
            data = {
                'header': pgettext('w_trading_new', 'Создание оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading_new', 'Достигнут лимит торговых предложений'),
            }
            return JsonResponse(data)

        # проверка, существует ли такой ресурс вообще
        good = request.POST.get('good')

        try:
            good = int(good)

        except ValueError:
            return {
                'header': pgettext('w_trading_new', 'Создание оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading_new', 'ID товара должен быть целым числом'),
            }

        if not Good.objects.filter(pk=good).exists() and not good == -1:
            data = {
                'header': pgettext('w_trading_new', 'Создание оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading_new', 'Указанный товар не существует'),
            }
            return JsonResponse(data)

        good_obj = None
        wild_pass = False

        if Good.objects.filter(pk=good).exists():
            # получим объект товара
            good_obj = Good.objects.get(pk=good)

        else:
            wild_pass = True

        # проверить, что количество товара в пределах Integer 0 < X < 2147483647
        count = request.POST.get('count')

        if not count.isdigit():
            data = {
                'header': pgettext('w_trading_new', 'Создание оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading_new', 'Количество - не число'),
            }
            return JsonResponse(data)

        count = int(count)

        if count <= 0:
            data = {
                'header': pgettext('w_trading_new', 'Создание оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading_new', 'Количество товара должно быть положительным числом'),
            }
            return JsonResponse(data)

        if count > 2147483647:
            data = {
                'header': pgettext('w_trading_new', 'Создание оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading_new', 'Количество товара слишком велико'),
            }
            return JsonResponse(data)

        # проверить, что цена товара в пределах BigInt 0 < X < 9223372036854775807
        price = int(request.POST.get('price'))

        if price <= 0:
            data = {
                'header': pgettext('w_trading_new', 'Создание оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading_new', 'Цена товара должна быть положительным числом'),
            }
            return JsonResponse(data)

        if price > 9223372036854775807:
            data = {
                'header': pgettext('w_trading_new', 'Создание оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading_new', 'Цена товара слишком велика'),
            }
            return JsonResponse(data)

        s_storage = Storage.actual.get(pk=int(souce_pk))
        lock = None
        cost = 0
        # если продажа:
        if action == 'sell':
            # Wild Pass
            if good == -1:
                # проверить, что у игрока хватает премиум-карт
                if count > getattr(player, 'cards_count'):
                    data = {
                        'header': pgettext('w_trading_new', 'Создание оффера'),
                        'grey_btn': pgettext('mining', 'Закрыть'),
                        'response': pgettext('w_trading_new', 'Недостаточно Wild Pass для продажи'),
                    }
                    return JsonResponse(data)

                WildpassLog = apps.get_model('player.WildpassLog')
                prem_log = WildpassLog(player=player, count=getattr(player, 'cards_count') - count,
                                       activity_txt='trading')
                prem_log.save()

                # списать товар со Склада
                setattr(player, 'cards_count', getattr(player, 'cards_count') - count)
                player.save()

            else:
                # проверить, что на указанном складе хватает указанного ресурса
                if not Stock.objects.filter(storage=s_storage, good=good_obj, stock__gte=count).exists():
                    data = {
                        'header': pgettext('w_trading_new', 'Создание оффера'),
                        'grey_btn': pgettext('mining', 'Закрыть'),
                        'response': pgettext('w_trading_new', 'Недостаточно ресурса для продажи'),
                    }
                    return JsonResponse(data)

                # списать товар со Склада
                stock = Stock.objects.select_for_update().get(storage=s_storage, good=good_obj, stock__gte=count)
                setattr(stock, 'stock', getattr(stock, 'stock') - count)
                stock.save()
                # заблокировать товар на указанном Складе
                lock = GoodLock(lock_storage=s_storage, lock_good=good_obj, lock_count=count)

        # если покупка:
        elif action == 'buy':
            # проверить, что произведение количества и цены меньше BigInt
            if count * price > 9223372036854775807:
                data = {
                    'header': pgettext('w_trading_new', 'Создание оффера'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('w_trading_new', 'Стоимость товара слишком велика'),
                }
                return JsonResponse(data)

            # проверить, что стоимость товара не больше налички игрока
            if count * price > player.cash:
                data = {
                    'header': pgettext('w_trading_new', 'Создание оффера'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('w_trading_new', 'Недостаточно средств'),
                }
                return JsonResponse(data)

            if not good == -1 and good_obj:
                # проверить наличие места на складе
                ret_stocks, ret_st_stocks = get_stocks(s_storage, [good_obj.name_ru, ])

                # узнаем размерность товара и сколько в этой размерности занято
                sizetype_stocks = ret_st_stocks[good_obj.size]

                if not s_storage.capacity_check(good_obj.size, count, sizetype_stocks):
                    data = {
                        'header': pgettext('w_trading_new', 'Создание оффера'),
                        'grey_btn': pgettext('mining', 'Закрыть'),
                        'response': pgettext('w_trading_new', 'Недостаточно места на складе для закупаемого товара'),
                    }
                    return JsonResponse(data)

                # добавляем к товару на складе место, которое занято скупками
                type_good_list = Good.objects.filter(size=good_obj.size)
                if TradeOffer.actual.filter(owner_storage=s_storage,
                                            count__gt=0, type='buy',
                                            offer_good__in=type_good_list
                                        ).exists():

                    sizetype_stocks += int(TradeOffer.actual.filter(
                        owner_storage=s_storage,
                        count__gt=0,
                        type='buy',
                        offer_good__in=type_good_list
                    ).aggregate(count_sum=Sum('count'))['count_sum'])

                    if not s_storage.capacity_check(good_obj.size, count, sizetype_stocks):
                        data = {
                            'header': pgettext('w_trading_new', 'Создание оффера'),
                            'grey_btn': pgettext('mining', 'Закрыть'),
                            'response': pgettext('w_trading_new',
                                                 'Недостаточно места на складе, с учётом других закупочных ордеров'),
                        }
                        return JsonResponse(data)

            cost = count * price
            # списать деньги с игрока
            setattr(player, 'cash', getattr(player, 'cash') - count * price)
            player.save()
            # заблокировать деньги на скупку ресурсов
            lock = CashLock(lock_player=player, lock_cash=count * price)

        # создать предложение
        offer = TradeOffer(
            owner_storage=s_storage,
            initial_volume=count,
            count=count,
            price=price,
            cost=cost,
            cost_count=cost,
            type=action,
            view_type='all',
            offer_good=good_obj,
            wild_pass=wild_pass,
            create_date=timezone.now()
        )
        offer.save()
        # для всех, кроме прем-карт
        if lock:
            lock.lock_offer = offer
            lock.save()

        data = {
            'header': pgettext('w_trading_new', 'Создание оффера'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': pgettext('w_trading_new', 'Торговое предложение успешно создано'),
            'success': 'True',
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'header': pgettext('w_trading_new', 'Создание оффера'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': pgettext('mining', 'Ошибка метода'),
        }
        return JsonResponse(data)
