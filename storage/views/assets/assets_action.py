import json
import math
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect

from player.decorators.player import check_player
from player.player import Player
from region.views.distance_counting import distance_counting
from storage.models.storage import Storage
from storage.views.storage.check_cap_exists import check_cap_exists
from storage.views.storage.check_goods_exists import check_goods_exists
from storage.views.storage.get_transfer_price import get_transfer_price
from storage.views.storage.transfer_values import transfer_values


# переименование партии
@login_required(login_url='/')
@check_player
@transaction.atomic
def assets_action(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.get(account=request.user)

        # узнаём действие, которое игрок хочет совершить
        action = request.POST.get('action')

        if action == 'transfer':
            # получаем целевой склад
            dest_pk = request.POST.get('dest_storage')

            if dest_pk == 'null':
                data = {
                    'response': 'Целевой Склад не заполнен',
                }
                return JsonResponse(data)

            # проверяем, есть ли целевой склад среди складов игрока
            storages = Storage.objects.filter(owner=player)
            storages_pk = []
            # словарь склад - словарь стоимости до других регионов со складами, как в assets.py
            trans_mul = {}

            for storage in storages:
                storages_pk.append(storage.pk)

                trans_mul[storage.pk] = {}
                for dest in storages:
                    if not dest == storage:
                        trans_mul[storage.pk][dest.pk] = math.ceil(distance_counting(storage.region, dest.region) / 100)

            if int(dest_pk) in storages_pk:

                storages_values = json.loads(request.POST.get('storages'))
                # проверяем, что все склады принадлежат игроку
                for i_storg in storages_values.keys():
                    if not int(i_storg) in storages_pk:
                        data = {
                            'response': 'Склад ' + i_storg + ' вам не принадлежит',
                        }
                        return JsonResponse(data)

                # если в целевом складе ничего не заполнено
                if not len(storages_values.get(dest_pk)):
                    value_exist = False
                    # идем по всем складам
                    for storg in storages_values.keys():
                        # если хоть в одном переданы ресурсы, все ок
                        if len(storages_values.get(storg)):
                            value_exist = True
                            break

                    if value_exist:
                        # проверяем наличие на Складах из JSON указанных товаров
                        status = False

                        status, ret_storg, good, required, exist = check_goods_exists(storages, storages_values)

                        if status:
                            # также нужно проверить, что в целевом Складе хватает места
                            status = False
                            status, good, sent, exist_cap = check_cap_exists(Storage.objects.get(pk=int(dest_pk)),
                                                                             storages_values)

                            if status:
                                # потом убедиться, что у игрока есть деньги, оплатить передачу ресурсов
                                price = get_transfer_price(trans_mul, int(dest_pk), storages_values)
                                if player.cash >= price:
                                    # оплата
                                    player.cash -= price
                                    player.save()
                                    # передача ресурсов
                                    transfer_values(Storage.objects.get(pk=int(dest_pk)), storages_values)

                                else:
                                    data = {
                                        'response': 'Недостаточно средств для оплаты доставки',
                                    }
                                    return JsonResponse(data)
                            else:
                                data = {
                                    'response': 'На складе в регионе ' + str(
                                        Storage.objects.get(pk=int(dest_pk)).region.region_name) +
                                                ' недостаточно места для товара ' + str(good) + '\n' +
                                                'Требуется: ' + str(sent) + ', в наличии: ' + str(exist_cap),
                                }
                                return JsonResponse(data)
                        else:
                            data = {
                                'response': 'На складе в регионе ' + str(ret_storg.region.region_name) +
                                            ' недостаточно товара ' + str(good) + ' для передачи.\n' +
                                            'Требуется: ' + str(required) + ', в наличии: ' + str(exist),
                            }
                            return JsonResponse(data)
                    else:
                        data = {
                            'response': 'Товары для передачи не выбраны',
                        }
                        return JsonResponse(data)
                else:
                    data = {
                        'response': 'В целевом Складе заполнены значения',
                    }
                    return JsonResponse(data)
            else:
                data = {
                    'response': 'Целевой Склад вам не принадлежит',
                }
                return JsonResponse(data)




        elif action == 'destroy':
            pass

        else:
            data = {
                'response': 'Некорректное действие',
            }
            return JsonResponse(data)

        # # находим Склад, с которого хотят списать материалы
        # if not Storage.objects.filter(pk=int(request.POST.get('storage'))):
        #     data = {
        #         'response': 'Не найден Склад',
        #     }
        #     return JsonResponse(data)

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
