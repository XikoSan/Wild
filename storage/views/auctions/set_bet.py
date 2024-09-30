from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse

from player.decorators.player import check_player
from player.player import Player
from storage.models.auction.auction_bet import AuctionBet
from storage.models.auction.auction_lot import AuctionLot
from storage.models.good_lock import GoodLock
from storage.models.storage import Storage
from storage.models.good import Good
from storage.models.stock import Stock
from django.utils.translation import pgettext

# переименование игрока
@login_required(login_url='/')
@check_player
@transaction.atomic
def set_bet(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        try:
            lot_id = int(request.POST.get('lot_id'))

        except ValueError:
            data = {
                'header': pgettext("auction", 'Лот - не число'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext("auction", 'ID лота должно быть числом'),
            }
            return JsonResponse(data)

        if not AuctionLot.actual.filter(pk=lot_id).exists():
            data = {
                'header': pgettext("auction", 'Лот не существует'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext("auction", 'Указанный лот не существует'),
            }
            return JsonResponse(data)

        lot = AuctionLot.actual.get(pk=lot_id)

        try:
            storage_id = int(request.POST.get('source'))

        except ValueError:
            data = {
                'header': pgettext("auction", 'Склад - не число'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext("auction", 'ID склада должно быть числом'),
            }
            return JsonResponse(data)

        if not Storage.actual.filter(pk=storage_id, owner=player).exists():
            data = {
                'header': pgettext("auction", 'Склад не существует'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext("auction", 'Указанный склад не существует'),
            }
            return JsonResponse(data)

        storage = Storage.actual.get(pk=storage_id, owner=player)

        # узнаем, хватает ли ресурса на выбранном складе
        if not Stock.objects.filter(storage=storage, good=lot.auction.good, stock__gte=lot.count).exists():
            data = {
                'header': pgettext("auction", 'Недостаточно товаров'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext("auction", 'На указанном складе недостаточно товара'),
            }
            return JsonResponse(data)

        stock = Stock.objects.get(storage=storage, good=lot.auction.good, stock__gte=lot.count)

        try:
            count = int(request.POST.get('count'))

        except ValueError:
            data = {
                'header': pgettext("auction", 'Цена - не число'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext("auction", 'Цена товара должна быть числом'),
            }
            return JsonResponse(data)

        current_bet = None
        if AuctionBet.actual.filter(auction_lot=lot).exists():
            current_bet = AuctionBet.actual.get(auction_lot=lot)

        if current_bet and count >= current_bet.price:
            data = {
                'header': pgettext("auction", 'Ставка слишком велика'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response':  pgettext("auction", 'Ставка должна быть меньше существующей'),
            }
            return JsonResponse(data)

        elif count > lot.start_price:
            data = {
                'header': pgettext("auction", 'Ставка слишком велика'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext("auction", 'Ставка должна быть не больше начальной'),
            }
            return JsonResponse(data)

        elif count < 1:
            data = {
                'header': pgettext("auction", 'Ставка слишком мала'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext("auction", 'Ставка должна быть не меньше 1'),
            }
            return JsonResponse(data)

        # setattr(storage, lot.auction.good, getattr(storage, lot.auction.good) - lot.count)
        stock.stock -= lot.count
        stock.save()

        good_lock = GoodLock(
            lock_storage=storage,
            lock_good=lot.auction.good,
            lock_count=lot.count
        )

        good_lock.save()

        new_bet = AuctionBet(
            auction_lot=lot,
            price=count,
            good_lock=good_lock
        )

        if current_bet:
            # возвращаем ресурсы из блокировки
            old_stock, created = Stock.objects.get_or_create(storage=current_bet.good_lock.lock_storage,
                                                         good=lot.auction.good
                                                         )
            old_stock.stock += lot.count
            old_stock.save()

            # удаляем блокировку
            current_bet.good_lock.deleted = True
            current_bet.good_lock.save()
            # удаляем ставку
            current_bet.deleted = True
            current_bet.save()

        new_bet.save()

        data = {
            'response': 'ok',
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('skills', 'Изучение навыка'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
