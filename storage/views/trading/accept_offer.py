from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from player.logs.print_log import log
from player.decorators.player import check_player
from player.player import Player
from region.views.distance_counting import distance_counting
from storage.models.cash_lock import CashLock
from storage.models.good_lock import GoodLock
from storage.models.storage import Storage
from storage.models.trade_offer import TradeOffer
import time
import math
from state.models.state import State
from storage.views.storage.locks.get_storage import get_stocks
from django.contrib.humanize.templatetags.humanize import number_format
from storage.models.trading_log import TradingLog
from player.logs.cash_log import CashLog
from storage.views.trading.premium_trading import premium_trading
from django.utils.translation import pgettext
from war.models.wars.war import War
from player.views.get_subclasses import get_subclasses
from storage.models.stock import Stock
from storage.models.good import Good
from region.building.infrastructure import Infrastructure
from region.views.find_route import find_route


@login_required(login_url='/')
@check_player
@transaction.atomic
# принять торговое предложение
def accept_offer(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.select_for_update().get(account=request.user)

        # получим требуемое количество товара
        count = 0
        try:
            count = int(request.POST.get('count'))

        except ValueError:
            data = {
                'header': pgettext('w_trading', 'Принятие оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'В поле количество должно быть число'),
            }
            return JsonResponse(data)

        if count <= 0:
            data = {
                'header': pgettext('w_trading', 'Принятие оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'В поле количество должно быть положительное число'),
            }
            return JsonResponse(data)

        # получим оффер
        offer_id = None
        try:
            offer_id = int(request.POST.get('id'))

        except ValueError:
            data = {
                'header': pgettext('w_trading', 'Принятие оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'ID оффера должно быть числом'),
            }
            return JsonResponse(data)

        # получим склад
        storage_id = None
        try:
            storage_id = int(request.POST.get('storage'))

        except ValueError:
            data = {
                'header': pgettext('w_trading', 'Принятие оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'ID склада должно быть числом'),
            }
            return JsonResponse(data)

        storage_region_pk = None
        if Storage.actual.filter(pk=storage_id, owner=player).exists():
            storage_region_pk = Storage.actual.get(pk=storage_id).region.pk

        else:
            data = {
                'header': pgettext('w_trading', 'Принятие оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'Выбранного склада игрока не существует'),
            }
            return JsonResponse(data)

        offer = None
        if TradeOffer.actual.filter(pk=offer_id, count__gt=0).exists():

            ex_kwargs = {}
            dest_regions = []
            dest_regions_buy = []
            war_classes = get_subclasses(War)
            for war_cl in war_classes:
                # исключение - тест войны
                if war_cl.__name__ == 'EventWar':
                    continue
                # если есть войны за этот рег
                if war_cl.objects.filter(running=True).exists():
                    # айдишники всех целевых регов
                    tmp_war_list = war_cl.objects.filter(running=True).values_list('def_region__pk')
                    for dest_pk in tmp_war_list:
                        if not dest_pk[0] in dest_regions:
                            # если целевой регион совпадает с регионом нашего склада, то пропускаем
                            # (торговля в пределах региона разрешена даже во время войны)
                            if dest_pk[0] != storage_region_pk:
                                dest_regions.append(dest_pk[0])
                            # список всех целей для ордеров скупки
                            dest_regions_buy.append(dest_pk[0])

            ex_kwargs['owner_storage__region__pk__in'] = dest_regions

            offer = TradeOffer.actual.select_for_update().get(pk=offer_id)

            if offer.type == 'sell':
                # если предложение не нашлось - значит, оно из другого региона, и там идет война
                if not TradeOffer.actual.filter(pk=offer_id, type='sell', count__gt=0).exclude(**ex_kwargs).exists():

                    data = {
                        'header': pgettext('w_trading', 'Принятие оффера'),
                        'grey_btn': pgettext('mining', 'Закрыть'),
                        'response': pgettext('w_trading', 'Нельзя принять оффер из атакованного региона'),
                    }
                    return JsonResponse(data)

            # если торговый ордер на скупку, то проверяем, что нашего региона нет в списке атакованных
            if offer.type == 'buy':
                if storage_region_pk in dest_regions_buy and storage_region_pk != offer.owner_storage.region.pk:

                    data = {
                        'header': pgettext('w_trading', 'Принятие оффера'),
                        'grey_btn': pgettext('mining', 'Закрыть'),
                        'response': pgettext('w_trading', 'Нельзя принять оффер из атакованного региона'),
                    }
                    return JsonResponse(data)

            if offer.owner_storage.owner == player:
                data = {
                    'header': pgettext('w_trading', 'Принятие оффера'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('w_trading', 'Нельзя принять собственный оффер'),
                }
                return JsonResponse(data)

            if offer.count < count:
                data = {
                    'header': pgettext('w_trading', 'Принятие оффера'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('w_trading', 'Оффер изменился, или вы ввели некорректное число'),
                }
                return JsonResponse(data)

        else:
            data = {
                'header': pgettext('w_trading', 'Принятие оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'Оффер не существует или уже принят'),
            }
            return JsonResponse(data)

        if offer.wild_pass:
            return premium_trading(player, count, offer)

        # ----------------------------------------------

        storage = None

        storage = Storage.actual.select_for_update().get(pk=storage_id)
        ret_stocks, ret_st_stocks = get_stocks(Storage.actual.select_for_update().get(pk=storage_id), [offer.offer_good.name_ru, ])

        # узнаем размерность товара и сколько в этой размерности занято
        sizetype_stocks = ret_st_stocks[offer.offer_good.size]

        if offer.type == 'sell' \
                and not storage.capacity_check(offer.offer_good.size, count, sizetype_stocks):
            data = {
                'header': pgettext('w_trading', 'Принятие оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'На выбранном складе недостаточно места для товара'),
            }
            return JsonResponse(data)

        elif offer.type == 'buy' \
                and not Stock.objects.filter(storage=storage, good=offer.offer_good, stock__gte=count).exists():
            data = {
                'header': pgettext('w_trading', 'Принятие оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'На выбранном складе недостаточно товара'),
            }
            return JsonResponse(data)

        # получим владельца склада
        offer_owner = None
        if Player.objects.filter(pk=offer.owner_storage.owner.pk).exists():

            offer_owner = Player.objects.select_for_update().get(pk=offer.owner_storage.owner.pk)

        else:
            data = {
                'header': pgettext('w_trading', 'Принятие оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'Выбранного склада игрока не существует'),
            }
            return JsonResponse(data)

        # считаем доставку
        trans_mul = math.ceil(distance_counting(storage.region, offer.owner_storage.region) / 100)
        # path, trans_mul = find_route(storage.region, offer.owner_storage.region)

        src_infr = Infrastructure.indexes[Infrastructure.get_stat(storage.region)[0]['top']]

        dest_infr = Infrastructure.indexes[Infrastructure.get_stat(offer.owner_storage.region)[0]['top']]

        delivery_price = math.ceil( math.ceil(int(count) * offer.offer_good.volume) * trans_mul * ( ( 100 - src_infr - dest_infr ) / 100 ) )

        # если оффер - продажа
        if offer.type == 'sell':
            #   проверяем наличие денег на указанное количество + доставка
            fin_sum = (count * offer.price) + delivery_price
            if player.cash < fin_sum:
                data = {
                    'header': pgettext('w_trading', 'Принятие оффера'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('w_trading', 'Недостаточно средств. Требуется $') + number_format(fin_sum),
                }
                return JsonResponse(data)
            #   списываем у игрока деньги
            player.cash -= fin_sum
            player.save()
            # получаем налог с прибыли продавца
            taxed_count = State.get_taxes(offer_owner.region, count * offer.price, 'trade', 'cash')
            #   начисляем продавцу деньги
            offer_owner.cash += taxed_count
            offer_owner.save()
            #   списываем из оффера товар
            offer.count -= count
            #   удаляем товар из связанной блокировки
            # получим блокировку ресурса
            offer_good_lock = None
            if GoodLock.objects.filter(lock_offer=offer, deleted=False).exists():

                offer_good_lock = GoodLock.objects.select_for_update().get(lock_offer=offer, deleted=False)

            else:
                data = {
                    'header': pgettext('w_trading', 'Принятие оффера'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('w_trading', 'Не удалось получить блокировку по офферу') + number_format(fin_sum),
                }
                return JsonResponse(data)

            offer_good_lock.lock_count -= count
            #   если удаляют весь товар из блокировки:
            if offer_good_lock.lock_count == 0:
                # закрыть блокировку
                offer_good_lock.deleted = True

            offer_good_lock.save()

            #   начисляем товар на склад игрока
            if Stock.objects.filter(storage=storage, good=offer.offer_good).exists():
                stock = Stock.objects.get(storage=storage, good=offer.offer_good)

            else:
                stock = Stock(
                                storage=storage,
                                good=offer.offer_good
                            )

            stock.stock += count
            stock.save()

            # создаем лог о покупке товара
            new_log = TradingLog.objects.create(
                player=player,
                cash_value=0 - (count * offer.price),
                delivery_value=delivery_price,
                player_storage=storage,
                good_value=count
            )
            offer.accepters.add(new_log)

            # создаем лог движения денег
            CashLog.create(player=player, cash=0 - fin_sum, activity_txt='trade')
            CashLog.create(player=offer_owner, cash=taxed_count, activity_txt='trade')

            #   если продажа закрывает оффер:
            if offer.count == 0:
                #       закрываем оффер
                offer.accept_date = timezone.now()
                offer.deleted = True

            offer.save()

        # если оффер - покупка
        elif offer.type == 'buy':
            #   проверяем наличие в ОФФЕРЕ и блокировке денег на количество (на всяк случай)
            offer_sum = count * offer.price

            # новички не платят налоги неделю
            if request.user.date_joined + timedelta(days=7) > timezone.now():
                taxed_sum = offer_sum
            else:
                # проверяем налог с прибыли продавца
                taxed_sum = State.check_taxes(player.region, offer_sum, 'trade')

            if taxed_sum < delivery_price:
                data = {
                    'header': pgettext('w_trading', 'Принятие оффера'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('w_trading', 'Ваши расходы на доставку больше прибыли'),
                }
                return JsonResponse(data)

            if offer.cost_count < offer_sum:
                data = {
                    'header': pgettext('w_trading', 'Принятие оффера'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('w_trading', 'В торговом предложении недостаточно средств'),
                }
                return JsonResponse(data)

            # получим блокировку денег
            offer_cash_lock = None
            if CashLock.objects.filter(lock_offer=offer, deleted=False).exists():
                offer_cash_lock = CashLock.objects.select_for_update().get(lock_offer=offer, deleted=False)
            else:
                data = {
                    'header': pgettext('w_trading', 'Принятие оффера'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('w_trading', 'Не удалось получить блокировку по офферу'),
                }
                return JsonResponse(data)

            if offer_cash_lock.lock_cash < offer_sum:
                data = {
                    'header': pgettext('w_trading', 'Принятие оффера'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('w_trading', 'В связанной блокировке недостаточно средств'),
                }
                return JsonResponse(data)

            #   проверяем у игрока наличие денег на доставку
            if player.cash + taxed_sum < delivery_price:
                data = {
                    'header': pgettext('w_trading', 'Принятие оффера'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('w_trading', 'Недостаточно средств. Требуется $') + number_format(delivery_price),
                }
                return JsonResponse(data)

            # получим склад продавца
            offer_storage = None
            if Storage.actual.filter(pk=offer.owner_storage.pk).exists():
                offer_storage = Storage.actual.select_for_update().get(pk=offer.owner_storage.pk)
            else:
                data = {
                    'header': pgettext('w_trading', 'Принятие оффера'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('w_trading', 'Выбранного склада оффера не существует'),
                }
                return JsonResponse(data)

            # получим склад продавца с учетом блокировок
            locks_stocks, ret_st_stocks = get_stocks(offer_storage, [offer.offer_good.name_ru, ])

            #   списываем из оффера деньги
            offer.cost_count -= offer_sum
            offer.save()

            #   удаляем деньги из связанной блокировки
            offer_cash_lock.lock_cash -= offer_sum

            #   если удаляют все деньги из блокировки:
            if offer_cash_lock.lock_cash == 0:
                #       закрыть блокировку
                offer_cash_lock.deleted = True
            offer_cash_lock.save()

            # получаем налог с прибыли продавца
            # новички не платят налоги неделю
            if request.user.date_joined + timedelta(days=7) > timezone.now():
                taxed_sum = offer_sum
            else:
                taxed_sum = State.get_taxes(player.region, offer_sum, 'trade', 'cash')

            #   начисляем деньги игроку
            player.cash += taxed_sum

            #   списываем с игрока деньги за доставку
            player.cash -= delivery_price
            player.save()

            #   списываем товар со склада
            stock = Stock.objects.get(storage=storage, good=offer.offer_good)
            stock.stock -= count
            stock.save()

            #   списываем из оффера товар
            offer.count -= count

            #   если продажа закрывает оффер:
            if offer.count == 0:
                #       закрываем оффер
                offer.accept_date = timezone.now()
                offer.deleted = True
            offer.save()

            #   начисляем товар на склад оффера
            sizetype_stocks = ret_st_stocks[offer.offer_good.size]

            if Stock.objects.filter(storage=offer_storage, good=offer.offer_good).exists():
                stock = Stock.objects.get(storage=offer_storage, good=offer.offer_good)

            else:
                stock = Stock(
                    storage=offer_storage,
                    good=offer.offer_good
                )

            if offer_storage.capacity_check(offer.offer_good.size, count, sizetype_stocks):
                stock.stock += count
                stock.save()

            else:
                fact_count = getattr(offer_storage, offer.offer_good.size + '_cap') - sizetype_stocks

                stock.stock += fact_count
                stock.save()

            stock.save()

            # создаем лог о покупке товара
            new_log = TradingLog.objects.create(
                player=player,
                cash_value=offer_sum,
                delivery_value=delivery_price,
                player_storage=storage,
                good_value=count
            )
            offer.accepters.add(new_log)

            # создаем логи движения денег
            CashLog.create(player=player, cash=taxed_sum - delivery_price, activity_txt='trade')

        else:
            data = {
                'header': pgettext('w_trading', 'Принятие оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'Оффера такого типа не существует'),
            }
            return JsonResponse(data)

        data = {
            'response': 'ok',
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'header': pgettext('w_trading', 'Принятие оффера'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': pgettext('core', 'Ошибка метода'),
        }
        return JsonResponse(data)
