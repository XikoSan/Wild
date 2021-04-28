from django.contrib.auth.decorators import login_required
from django.db import transaction
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
@transaction.atomic
# новое торговое предложение
def create_offer(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.get(account=request.user)

        # узнаём действие, которое игрок хочет совершить
        action = request.POST.get('action')

        if not (action == 'sell' or action == 'buy'):
            data = {
                'header': 'Ошибка при создании',
                'grey_btn': 'Закрыть',
                'response': 'Некорректное действие',
            }
            return JsonResponse(data)

        # получаем целевой склад
        souce_pk = request.POST.get('storage')

        if not souce_pk.isdigit():
            data = {
                'header': 'Ошибка при создании',
                'grey_btn': 'Закрыть',
                'response': 'Склад не заполнен',
            }
            return JsonResponse(data)

        # проверяем, есть ли целевой склад среди складов игрока
        storages = Storage.objects.filter(owner=player)
        storages_pk = []

        for storage in storages:
            storages_pk.append(storage.pk)

        if int(souce_pk) in storages_pk:
            # проверка, существует ли такой ресурс вообще
            good = request.POST.get('good')
            if not hasattr(Storage, good):
                data = {
                    'header': 'Ошибка при создании',
                    'grey_btn': 'Закрыть',
                    'response': 'Указанный товар не существует',
                }
                return JsonResponse(data)

            # проверить, что количество товара в пределах Integer 0 < X < 2147483647
            count = int(request.POST.get('count'))

            if count <= 0:
                data = {
                    'header': 'Ошибка при создании',
                    'grey_btn': 'Закрыть',
                    'response': 'Количество товара должно быть положительным числом',
                }
                return JsonResponse(data)

            if count > 2147483647:
                data = {
                    'header': 'Ошибка при создании',
                    'grey_btn': 'Закрыть',
                    'response': 'Количество товара слишком велико',
                }
                return JsonResponse(data)

            # проверить, что цена товара в пределах BigInt 0 < X < 9223372036854775807
            price = int(request.POST.get('price'))

            if price <= 0:
                data = {
                    'header': 'Ошибка при создании',
                    'grey_btn': 'Закрыть',
                    'response': 'Цена товара должно быть положительным числом',
                }
                return JsonResponse(data)

            if price > 9223372036854775807:
                data = {
                    'header': 'Ошибка при создании',
                    'grey_btn': 'Закрыть',
                    'response': 'Цена товара слишком велика',
                }
                return JsonResponse(data)

            s_storage = Storage.objects.get(pk=int(souce_pk))
            lock = None
            cost = 0
            # если продажа:
            if action == 'sell':
                # проверить, что на указанном складе хватает указанного ресурса
                if count > getattr(s_storage, good):
                    data = {
                        'header': 'Ошибка при создании',
                        'grey_btn': 'Закрыть',
                        'response': 'Недостаточно ресурса для продажи',
                    }
                    return JsonResponse(data)
                # списать товар со Склада
                setattr(s_storage, good, getattr(s_storage, good) - count)
                s_storage.save()
                # заблокировать товар на указанном Складе
                lock = GoodLock(lock_storage=s_storage, lock_good=good, lock_count=count)

            # если покупка:
            elif action == 'buy':
                # проверить, что произведение количества и цены меньше BigInt
                if count * price > 9223372036854775807:
                    data = {
                        'header': 'Ошибка при создании',
                        'grey_btn': 'Закрыть',
                        'response': 'Стоимость товара слишком велика',
                    }
                    return JsonResponse(data)
                # проверить, что стоимость товара не больше налички игрока
                if count * price > player.cash:
                    data = {
                        'header': 'Ошибка при создании',
                        'grey_btn': 'Закрыть',
                        'response': 'Недостаточно средств',
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
                good=good,
                create_date=timezone.now()
            )
            offer.save()
            lock.lock_offer = offer
            lock.save()

        else:
            data = {
                'header': 'Ошибка при создании',
                'response': 'Указанный Склад вам не принадлежит',
                'grey_btn': 'Закрыть',
            }
            return JsonResponse(data)

        data = {
            'header': 'Предложение создано',
            'response': 'Торговое предложение успешно создано',
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
