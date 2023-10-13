from django.contrib.humanize.templatetags.humanize import number_format
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone

from player.logs.cash_log import CashLog
from player.player import Player
from state.models.state import State
from storage.models.cash_lock import CashLock
from storage.models.trading_log import TradingLog
from django.utils.translation import pgettext


@transaction.atomic
# торговля премами
def premium_trading(player, count, offer):
    # получим владельца склада
    offer_owner = None
    if Player.objects.filter(pk=offer.owner_storage.owner.pk).exists():

        offer_owner = Player.objects.select_for_update().get(pk=offer.owner_storage.owner.pk)

    else:
        data = {
            'header': pgettext('w_trading', 'Торговля Wild Pass'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': pgettext('w_trading', 'Не удалось получить владельца торгового предложения'),
        }
        return JsonResponse(data)

    # если оффер - продажа
    if offer.type == 'sell':
        #   проверяем наличие денег на указанное количество + доставка
        fin_sum = count * offer.price
        if player.cash < fin_sum:
            data = {
                'header': pgettext('w_trading', 'Торговля Wild Pass'),
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

        #   начисляем товар игроку
        setattr(player, 'cards_count', getattr(player, 'cards_count') + count)
        player.save()

        # создаем лог о покупке товара
        new_log = TradingLog.objects.create(
            player=player,
            cash_value=0 - (count * offer.price),
            player_storage=offer.owner_storage,
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

        if getattr(player, 'cards_count') < count:
            data = {
                'header': pgettext('w_trading', 'Торговля Wild Pass'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'У вас недостаточно Wild Pass'),
            }
            return JsonResponse(data)

        #   проверяем наличие в ОФФЕРЕ и блокировке денег на количество (на всяк случай)
        offer_sum = count * offer.price
        # проверяем налог с прибыли продавца
        if request.user.date_joined + timedelta(days=7) > timezone.now():
            taxed_sum = offer_sum
        else:
            taxed_sum = State.check_taxes(player.region, offer_sum, 'trade')

        if offer.cost_count < offer_sum:
            data = {
                'header': pgettext('w_trading', 'Торговля Wild Pass'),
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
                'header': pgettext('w_trading', 'Торговля Wild Pass'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'Не удалось получить блокировку по офферу'),
            }
            return JsonResponse(data)

        if offer_cash_lock.lock_cash < offer_sum:
            data = {
                'header': pgettext('w_trading', 'Торговля Wild Pass'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('w_trading', 'В связанной блокировке недостаточно средств'),
            }
            return JsonResponse(data)

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
        if request.user.date_joined + timedelta(days=7) > timezone.now():
            taxed_sum = offer_sum
        else:
            taxed_sum = State.get_taxes(player.region, offer_sum, 'trade', 'cash')

        #   начисляем деньги игроку
        player.cash += taxed_sum

        #   списываем товар со склада
        setattr(player, 'cards_count', getattr(player, 'cards_count') - count)
        player.save()

        #   списываем из оффера товар
        offer.count -= count

        #   если продажа закрывает оффер:
        if offer.count == 0:
            #       закрываем оффер
            offer.accept_date = timezone.now()
            offer.deleted = True
        offer.save()

        #   начисляем товар на склад оффера
        setattr(offer_owner, 'cards_count', getattr(offer_owner, 'cards_count') + count)

        offer_owner.save()

        # создаем лог о покупке товара
        new_log = TradingLog.objects.create(
            player=player,
            cash_value=offer_sum,
            player_storage=offer.owner_storage,
            good_value=count
        )
        offer.accepters.add(new_log)

        # создаем логи движения денег
        CashLog.create(player=player, cash=taxed_sum, activity_txt='trade')

    else:
        data = {
            'header': pgettext('w_trading', 'Торговля Wild Pass'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': pgettext('w_trading', 'Оффера такого типа не существует'),
        }
        return JsonResponse(data)

    data = {
        'header': pgettext('w_trading', 'Торговля Wild Pass'),
        'grey_btn': pgettext('mining', 'Закрыть'),
        'response': pgettext('w_trading', 'Торговое предложение успешно принято'),
    }
    return JsonResponse(data)
