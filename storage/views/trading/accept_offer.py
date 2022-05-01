from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
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
from storage.views.storage.get_transfer_price import get_transfer_price
from storage.views.storage.locks.get_storage import get_storage
from django.contrib.humanize.templatetags.humanize import number_format
from storage.models.trading_log import TradingLog
from player.logs.cash_log import CashLog
from storage.views.trading.premium_trading import premium_trading


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
                'header': 'Количество - не число',
                'grey_btn': 'Закрыть',
                'response': 'В поле количество должно быть число',
            }
            return JsonResponse(data)

        if count <= 0:
            data = {
                'header': 'Ошибка количества',
                'grey_btn': 'Закрыть',
                'response': 'В поле количество должно быть положительное число',
            }
            return JsonResponse(data)

        # получим оффер
        offer_id = None
        try:
            offer_id = int(request.POST.get('id'))

        except ValueError:
            data = {
                'header': 'Оффер - не число',
                'grey_btn': 'Закрыть',
                'response': 'ID оффера должно быть числом',
            }
            return JsonResponse(data)

        offer = None
        if TradeOffer.actual.filter(pk=offer_id, count__gt=0).exists():

            offer = TradeOffer.actual.select_for_update().get(pk=offer_id)

            if offer.owner_storage.owner == player:
                data = {
                    'header': 'Свой оффер',
                    'grey_btn': 'Закрыть',
                    'response': 'Нельзя принять собственный оффер',
                }
                return JsonResponse(data)

            if offer.count < count:
                data = {
                    'header': 'Товара в оффере недостаточно',
                    'grey_btn': 'Закрыть',
                    'response': 'Оффер изменился, или вы ввели некорректное число',
                }
                return JsonResponse(data)

        else:
            data = {
                'header': 'Нет оффера',
                'grey_btn': 'Закрыть',
                'response': 'Оффер не существует или уже принят',
            }
            return JsonResponse(data)

        if offer.good == 'wild_pass':
            return premium_trading(player, count, offer)

        # получим склад
        storage_id = None
        try:
            storage_id = int(request.POST.get('storage'))

        except ValueError:
            data = {
                'header': 'Склад - не число',
                'grey_btn': 'Закрыть',
                'response': 'ID склада должно быть числом',
            }
            return JsonResponse(data)

        storage = None
        lock_storage = None
        if Storage.actual.filter(pk=storage_id).exists():

            storage = Storage.actual.select_for_update().get(pk=storage_id)
            lock_storage = get_storage(Storage.actual.select_for_update().get(pk=storage_id), [offer.good, ])

            if offer.type == 'sell' \
                    and not lock_storage.capacity_check(offer.good, count):
                data = {
                    'header': 'Недостаточно места',
                    'grey_btn': 'Закрыть',
                    'response': 'На выбранном складе недостаточно места для товара',
                }
                return JsonResponse(data)

            elif offer.type == 'buy' \
                    and getattr(storage, offer.good) < count:
                data = {
                    'header': 'Недостаточно товара',
                    'grey_btn': 'Закрыть',
                    'response': 'На выбранном складе недостаточно товара',
                }
                return JsonResponse(data)

        else:
            data = {
                'header': 'Нет склада игрока',
                'grey_btn': 'Закрыть',
                'response': 'Выбранного склада игрока не существует',
            }
            return JsonResponse(data)

        # получим владельца склада
        offer_owner = None
        if Player.objects.filter(pk=offer.owner_storage.owner.pk).exists():

            offer_owner = Player.objects.select_for_update().get(pk=offer.owner_storage.owner.pk)

        else:
            data = {
                'header': 'Получение владельца',
                'grey_btn': 'Закрыть',
                'response': 'Не удалось получить владельца Склада',
            }
            return JsonResponse(data)

        # считаем доставку
        trans_mul = {storage.pk: {}}
        trans_mul[storage.pk][offer.owner_storage.pk] = math.ceil(
            distance_counting(storage.region, offer.owner_storage.region) / 100)

        offer_value = {str(offer.owner_storage.pk): {}}
        offer_value[str(offer.owner_storage.pk)][offer.good] = count

        price, prices = get_transfer_price(trans_mul, int(storage.pk), offer_value)

        # если оффер - продажа
        if offer.type == 'sell':
            #   проверяем наличие денег на указанное количество + доставка
            fin_sum = (count * offer.price) + price
            if player.cash < fin_sum:
                data = {
                    'header': 'Недостаточно средств',
                    'response': 'Недостаточно средств. Требуется $' + number_format(fin_sum),
                    'grey_btn': 'Закрыть',
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
                    'header': 'Получение блокировки',
                    'grey_btn': 'Закрыть',
                    'response': 'Не удалось получить блокировку по офферу',
                }
                return JsonResponse(data)

            offer_good_lock.lock_count -= count
            #   если удаляют весь товар из блокировки:
            if offer_good_lock.lock_count == 0:
                # закрыть блокировку
                offer_good_lock.deleted = True

            offer_good_lock.save()

            #   начисляем товар на склад игрока
            setattr(storage, offer.good, getattr(storage, offer.good) + count)
            storage.save()

            # создаем лог о покупке товара
            new_log = TradingLog.objects.create(
                player=player,
                cash_value=0 - (count * offer.price),
                delivery_value=price,
                player_storage=storage,
                good_value=count
            )
            offer.accepters.add(new_log)

            # создаем лог движения денег
            CashLog(player=player, cash=0 - fin_sum, activity_txt='trade').save()
            CashLog(player=offer_owner, cash=taxed_count, activity_txt='trade').save()

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
            # проверяем налог с прибыли продавца
            taxed_sum = State.check_taxes(player.region, offer_sum, 'trade')

            if taxed_sum < price:
                data = {
                    'header': 'Запрет торговли в минус',
                    'response': 'Ваши расходы на доставку больше прибыли',
                    'grey_btn': 'Закрыть',
                }
                return JsonResponse(data)

            if offer.cost_count < offer_sum:
                data = {
                    'header': 'Недостаточно средств',
                    'response': 'В торговом предложении недостаточно средств',
                    'grey_btn': 'Закрыть',
                }
                return JsonResponse(data)

            # получим блокировку денег
            offer_cash_lock = None
            if CashLock.objects.filter(lock_offer=offer, deleted=False).exists():
                offer_cash_lock = CashLock.objects.select_for_update().get(lock_offer=offer, deleted=False)
            else:
                data = {
                    'header': 'Получение блокировки',
                    'grey_btn': 'Закрыть',
                    'response': 'Не удалось получить блокировку по офферу',
                }
                return JsonResponse(data)

            if offer_cash_lock.lock_cash < offer_sum:
                data = {
                    'header': 'Недостаточно средств',
                    'response': 'В связанной блокировке недостаточно средств',
                    'grey_btn': 'Закрыть',
                }
                return JsonResponse(data)

                #   проверяем у игрока наличие денег на доставку
            if player.cash + taxed_sum < price:
                data = {
                    'header': 'Недостаточно средств на оплату доставки',
                    'response': 'Недостаточно средств. Требуется $' + number_format(price),
                    'grey_btn': 'Закрыть',
                }
                return JsonResponse(data)

            # получим склад продавца
            offer_storage = None
            if Storage.actual.filter(pk=offer.owner_storage.pk).exists():
                offer_storage = Storage.actual.select_for_update().get(pk=offer.owner_storage.pk)
            else:
                data = {
                    'header': 'Нет склада оффера',
                    'grey_btn': 'Закрыть',
                    'response': 'Выбранного склада оффера не существует',
                }
                return JsonResponse(data)

            # получим склад продавца с учетом блокировок
            lock_offer_storage = get_storage(Storage.actual.select_for_update().get(pk=offer_storage.pk),
                                             [offer.good, ])

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
            taxed_sum = State.get_taxes(player.region, offer_sum, 'trade', 'cash')

            #   начисляем деньги игроку
            player.cash += taxed_sum

            #   списываем с игрока деньги за доставку
            player.cash -= price
            player.save()

            #   списываем товар со склада
            setattr(storage, offer.good, getattr(storage, offer.good) - count)
            storage.save()

            #   списываем из оффера товар
            offer.count -= count

            #   если продажа закрывает оффер:
            if offer.count == 0:
                #       закрываем оффер
                offer.accept_date = timezone.now()
                offer.deleted = True
            offer.save()

            #   начисляем товар на склад оффера
            if lock_offer_storage.capacity_check(offer.good, count):
                setattr(offer_storage, offer.good, getattr(offer_storage, offer.good) + count)
            else:
                setattr(offer_storage, offer.good, getattr(offer_storage, offer.good) + (
                            getattr(offer_storage, offer.good + '_cap') - getattr(lock_offer_storage, offer.good)))

            offer_storage.save()

            # создаем лог о покупке товара
            new_log = TradingLog.objects.create(
                player=player,
                cash_value=offer_sum,
                delivery_value=price,
                player_storage=storage,
                good_value=count
            )
            offer.accepters.add(new_log)

            # создаем логи движения денег
            CashLog(player=player, cash=taxed_sum - price, activity_txt='trade').save()

        else:
            data = {
                'header': 'Неверный тип оффера',
                'response': 'Оффера такого типа не существует',
                'grey_btn': 'Закрыть',
            }
            return JsonResponse(data)

        data = {
            'header': 'Предложение принято',
            'response': 'Торговое предложение успешно принято',
            'grey_btn': 'Закрыть',
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'header': 'Ошибка при создании',
            'grey_btn': 'Закрыть',
            'response': 'Ты уверен что тебе сюда, путник?',
        }
        return JsonResponse(data)
