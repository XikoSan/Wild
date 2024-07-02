from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.player import Player
from storage.models.storage import Storage
from django.utils.translation import pgettext
from war.models.wars.war import War
from player.views.get_subclasses import get_subclasses


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
                data = {
                    'header': pgettext('storage', 'Передача денег'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('storage', 'Отрицательное число денег игрока'),
                }
                return JsonResponse(data)

        # нет юнита в запросе, ищем дальше
        except ValueError:
            data = {
                'header': pgettext('storage', 'Передача денег'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('storage', 'Некорректное число денег игрока'),
            }
            return JsonResponse(data)

        new_storage = request.POST.get('cash_at_storage', '')
        # проверяем что передано целое положительное число
        try:
            new_storage_cnt = int(new_storage)
            # передано отрицательное число
            if new_storage_cnt < 0:
                data = {
                    'header': pgettext('storage', 'Передача денег'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('storage', 'Отрицательное число денег Склада'),
                }
                return JsonResponse(data)
            
        # нет юнита в запросе, ищем дальше
        except ValueError:
            data = {
                'header': pgettext('storage', 'Передача денег'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('storage', 'Некорректное число денег Склада'),
            }
            return JsonResponse(data)

        # если у игрока в этом регионе есть Склад
        if not Storage.actual.filter(owner=player, region=player.region).exists():
            data = {
                'header': pgettext('storage', 'Передача денег'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('storage', 'В этом регионе нет Склада'),
            }
            return JsonResponse(data)
        
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

                    # если идет война за этот регион
                    war_there = False
                    war_classes = get_subclasses(War)
                    for war_cl in war_classes:
                        # исключение - тест войны
                        if war_cl.__name__ == 'EventWar':
                            continue
                        # если есть войны за этот рег
                        if war_cl.objects.filter(running=True, def_region=storage.region).exists():
                            war_there = True
                            break
                    # нельзя выводить наличку из атакованного рега
                    if war_there and int(new_storage) < storage.cash:
                        data = {
                            'header': pgettext('storage', 'Передача денег'),
                            'grey_btn': pgettext('mining', 'Закрыть'),
                            'response': pgettext('storage', 'Нельзя вывести деньги из атакованного региона'),
                        }
                        return JsonResponse(data)

                    # обновляем данные игрока
                    Player.objects.filter(pk=player.pk).update(
                        cash=int(new_wallet))
                    # логируем
                    CashLog.create(player=player, cash=int(new_wallet) - player.cash, activity_txt='store')
                    # обновляем данные склада
                    Storage.actual.filter(pk=storage.pk).update(
                        cash=int(new_storage))
                    return HttpResponse('ok')


                
                else:
                    data = {
                        'header': pgettext('storage', 'Передача денег'),
                        'grey_btn': pgettext('mining', 'Закрыть'),
                        'response': pgettext('storage', 'Данные кошелька не совпадают с введенными'),
                    }
                    return JsonResponse(data)

            else:
                data = {
                    'header': pgettext('storage', 'Передача денег'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('storage', 'Недопустим ввод отрицательных чисел'),
                }
                return JsonResponse(data)
            
        else:
            return HttpResponse('ok')

    # если страницу только грузят
    else:
        data = {
            'header': pgettext('storage', 'Передача денег'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': pgettext('mining', 'Ошибка метода'),
        }
        return JsonResponse(data)
