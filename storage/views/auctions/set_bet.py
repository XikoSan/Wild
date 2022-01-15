from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse

from player.decorators.player import check_player
from player.player import Player
from storage.models.auction.auction_bet import AuctionBet
from storage.models.auction.auction_lot import AuctionLot
from storage.models.good_lock import GoodLock
from storage.models.storage import Storage


# переименование игрока
@login_required(login_url='/')
@check_player
@transaction.atomic
def set_bet(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.get(account=request.user)

        try:
            lot_id = int(request.POST.get('lot_id'))

        except ValueError:
            data = {
                'header': 'Лот - не число',
                'grey_btn': 'Закрыть',
                'response': 'ID лота должно быть числом',
            }
            return JsonResponse(data)

        if not AuctionLot.actual.filter(pk=lot_id).exists():
            data = {
                'header': 'Лот не существует',
                'grey_btn': 'Закрыть',
                'response': 'Указанный лот не существует',
            }
            return JsonResponse(data)

        lot = AuctionLot.actual.get(pk=lot_id)

        try:
            storage_id = int(request.POST.get('source'))

        except ValueError:
            data = {
                'header': 'Склад - не число',
                'grey_btn': 'Закрыть',
                'response': 'ID склада должно быть числом',
            }
            return JsonResponse(data)

        if not Storage.actual.filter(pk=storage_id, owner=player).exists():
            data = {
                'header': 'Склад не существует',
                'grey_btn': 'Закрыть',
                'response': 'Указанный склад не существует',
            }
            return JsonResponse(data)

        storage = Storage.actual.get(pk=storage_id, owner=player)

        # узнаем, хватает ли ресурса на выбранном складе
        if getattr(storage, lot.auction.good) < lot.count:
            data = {
                'header': 'Недостаточно товаров',
                'grey_btn': 'Закрыть',
                'response': 'На указанном складе недостаточно товара',
            }
            return JsonResponse(data)

        try:
            count = int(request.POST.get('count'))

        except ValueError:
            data = {
                'header': 'Цена - не число',
                'grey_btn': 'Закрыть',
                'response': 'Цена товара должна быть числом',
            }
            return JsonResponse(data)

        current_bet = None
        if AuctionBet.actual.filter(auction_lot=lot).exists():
            current_bet = AuctionBet.actual.get(auction_lot=lot)

        if current_bet and count >= current_bet.price:
            data = {
                'header': 'Ставка слишком велика',
                'grey_btn': 'Закрыть',
                'response': 'Ставка должна быть меньше существующей',
            }
            return JsonResponse(data)

        elif count > lot.start_price:
            data = {
                'header': 'Ставка слишком велика',
                'grey_btn': 'Закрыть',
                'response': 'Ставка должна быть не больше начальной',
            }
            return JsonResponse(data)

        elif count < 1:
            data = {
                'header': 'Ставка слишком мала',
                'grey_btn': 'Закрыть',
                'response': 'Ставка должна быть не меньше 1',
            }
            return JsonResponse(data)

        setattr(storage, lot.auction.good, getattr(storage, lot.auction.good) - lot.count)
        storage.save()

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
            setattr(current_bet.good_lock.lock_storage, lot.auction.good,
                    getattr(current_bet.good_lock.lock_storage, lot.auction.good) + current_bet.good_lock.lock_count)
            current_bet.good_lock.lock_storage.save()
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
            'response': 'Ты уверен что тебе сюда, путник?',
        }
        return JsonResponse(data)
