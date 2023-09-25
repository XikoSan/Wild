import math
import time
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import number_format
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.logs.print_log import log
from player.player import Player
from region.views.distance_counting import distance_counting
from storage.models.cash_lock import CashLock
from storage.models.good import Good
from storage.models.good_lock import GoodLock
from storage.models.stock import Stock
from storage.models.storage import Storage
from storage.models.trade_offer import TradeOffer
from storage.models.trading_log import TradingLog
from storage.views.storage.get_transfer_price import get_transfer_price
from storage.views.storage.locks.get_storage import get_storage


@login_required(login_url='/')
@check_player
@transaction.atomic
# принять торговое предложение
def cancel_offer(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        # получим оффер
        offer_id = None
        try:
            offer_id = int(request.POST.get('id'))

        except ValueError:
            data = {
                'header': pgettext('w_trading', 'Отмена оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'ID оффера должно быть числом'),
            }
            return JsonResponse(data)

        offer = None
        if TradeOffer.actual.filter(pk=offer_id, count__gt=0).exists():

            offer = TradeOffer.actual.select_for_update().get(pk=offer_id)

            if not offer.owner_storage.owner == player:
                data = {
                    'header': pgettext('w_trading', 'Отмена оффера'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('w_trading', 'Можно отменить только свой собственный оффер'),
                }
                return JsonResponse(data)

        else:
            data = {
                'header': pgettext('w_trading', 'Отмена оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'Оффер не существует или уже принят'),
            }
            return JsonResponse(data)

        # получим склад
        storage_id = None
        try:
            storage_id = int(offer.owner_storage.pk)

        except ValueError:
            data = {
                'header': pgettext('w_trading', 'Отмена оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'ID склада должно быть числом'),
            }
            return JsonResponse(data)

        storage = None
        if Storage.actual.filter(pk=storage_id).exists():

            storage = Storage.actual.select_for_update().get(pk=storage_id)

        else:
            data = {
                'header': pgettext('w_trading', 'Отмена оффера'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'Выбранного склада игрока не существует'),
            }
            return JsonResponse(data)

        if offer.type == 'sell':
            if offer.wild_pass:
                setattr(player, 'cards_count', getattr(player, 'cards_count') + offer.count)
                player.save()

            else:
                # получим блокировку ресурса
                offer_good_lock = None
                if GoodLock.objects.filter(lock_offer=offer, deleted=False).exists():
                    offer_good_lock = GoodLock.objects.select_for_update().get(lock_offer=offer, deleted=False)
                else:
                    data = {
                        'header': pgettext('w_trading', 'Отмена оффера'),
                        'grey_btn': pgettext('mining', 'Закрыть'),
                        'response': pgettext('w_trading', 'Не удалось получить блокировку по офферу'),
                    }
                    return JsonResponse(data)

                # setattr(storage, offer.good, getattr(storage, offer.good) + offer_good_lock.lock_count)
                # storage.save()

                #   начисляем товар на склад оффера
                if Stock.objects.filter(storage=storage, good=offer.offer_good).exists():
                    stock = Stock.objects.get(storage=storage, good=offer.offer_good)

                else:
                    stock = Stock(
                        storage=storage,
                        good=offer.offer_good
                    )

                stock.stock += offer.count
                stock.save()

                offer_good_lock.deleted = True
                offer_good_lock.save()

        else:
            # получим блокировку денег
            offer_cash_lock = None
            if CashLock.objects.filter(lock_offer=offer, deleted=False).exists():
                offer_cash_lock = CashLock.objects.select_for_update().get(lock_offer=offer, deleted=False)
            else:
                data = {
                    'header': pgettext('w_trading', 'Отмена оффера'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('w_trading', 'Не удалось получить блокировку по офферу'),
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
            'header': pgettext('w_trading', 'Отмена оффера'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': pgettext('mining', 'Ошибка метода'),
        }
        return JsonResponse(data)
