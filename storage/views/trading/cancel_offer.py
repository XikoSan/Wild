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
from storage.views.storage.get_transfer_price import get_transfer_price
from storage.views.storage.locks.get_storage import get_storage
from django.contrib.humanize.templatetags.humanize import number_format
from storage.models.trading_log import TradingLog
from player.logs.cash_log import CashLog


@login_required(login_url='/')
@check_player
@transaction.atomic
# принять торговое предложение
def cancel_offer(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.select_for_update().get(account=request.user)

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

            if not offer.owner_storage.owner == player:
                data = {
                    'header': 'Только свой оффер',
                    'grey_btn': 'Закрыть',
                    'response': 'Можно отменить только свой собственный оффер',
                }
                return JsonResponse(data)

        else:
            data = {
                'header': 'Нет оффера',
                'grey_btn': 'Закрыть',
                'response': 'Оффер не существует или уже принят',
            }
            return JsonResponse(data)

        # получим склад
        storage_id = None
        try:
            storage_id = int(offer.owner_storage.pk)

        except ValueError:
            data = {
                'header': 'Склад - не число',
                'grey_btn': 'Закрыть',
                'response': 'ID склада должно быть числом',
            }
            return JsonResponse(data)

        storage = None
        if Storage.actual.filter(pk=storage_id).exists():

            storage = Storage.actual.select_for_update().get(pk=storage_id)

        else:
            data = {
                'header': 'Нет склада игрока',
                'grey_btn': 'Закрыть',
                'response': 'Выбранного склада игрока не существует',
            }
            return JsonResponse(data)

        if offer.type == 'sell':
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

            setattr(storage, offer.good, getattr(storage, offer.good) + offer_good_lock.lock_count)
            storage.save()

            offer_good_lock.deleted = True
            offer_good_lock.save()

        else:
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

            player.cash += offer_cash_lock.lock_cash
            player.save()

            offer_cash_lock.deleted = True
            offer_cash_lock.save()

        offer.accept_date = timezone.now()
        offer.deleted = True
        offer.save()

        data = {
            'response': 'ok',
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
