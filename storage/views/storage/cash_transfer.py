from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.player import Player
from storage.models.storage import Storage


# передача денег со склада/на склад
@login_required(login_url='/')
@check_player
@transaction.atomic
def cash_transfer(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        # новые значения денег в кошельке и складе
        new_wallet = request.POST.get('cash_at_player', '')
        # проверяем что передано целое положительное число
        try:
            new_wallet_cnt = int(new_wallet)
            # передано отрицательное число
            if new_wallet_cnt < 0:
                return HttpResponse(_('Отрицательное число денег игрока'), content_type='text/html')
        # нет юнита в запросе, ищем дальше
        except ValueError:
            return HttpResponse(_('Некорректное число денег игрока'), content_type='text/html')

        new_storage = request.POST.get('cash_at_storage', '')
        # проверяем что передано целое положительное число
        try:
            new_storage_cnt = int(new_storage)
            # передано отрицательное число
            if new_storage_cnt < 0:
                return HttpResponse(_('Отрицательное число денег Склада'), content_type='text/html')
        # нет юнита в запросе, ищем дальше
        except ValueError:
            return HttpResponse(_('Некорректное число денег Склада'), content_type='text/html')

        # если у игрока в этом регионе есть Склад
        if not Storage.actual.filter(owner=player, region=player.region).exists():
            return HttpResponse(_('В этом регионе нет Склада'), content_type='text/html')
        # склад игрока
        storage = Storage.actual.get(owner=player, region=player.region)
        # проверки:
        # что количество денег до и после в обоих точках изменилось
        if player.cash != int(new_wallet) \
                and storage.cash != int(new_storage):
            # что оба значения не отрицательны
            if int(new_wallet) >= 0 \
                    and int(new_storage) >= 0:
                # что количество денег в сумме не изменилось
                if player.cash + storage.cash == int(new_wallet) + int(new_storage):
                    # обновляем данные игрока
                    Player.objects.filter(pk=player.pk).update(
                        cash=int(new_wallet))
                    # логируем
                    CashLog(player=player, cash=int(new_wallet) - player.cash, activity_txt='store').save()
                    # обновляем данные склада
                    Storage.actual.filter(pk=storage.pk).update(
                        cash=int(new_storage))
                    return HttpResponse('ok')
                else:
                    return HttpResponse(_('Данные кошелька не совпадают с введенными'), content_type='text/html')
                    # return HttpResponse('Данные кошелька не совпадают с введенными', content_type='text/html')
            else:
                return HttpResponse(_('Недопустим ввод отрицательных чисел'), content_type='text/html')
            # 'Недопустим ввод отрицательных чисел'
        else:
            return HttpResponse('ok')

    # если страницу только грузят
    else:
        return HttpResponse(_('incorrect_method'), content_type='text/html')
