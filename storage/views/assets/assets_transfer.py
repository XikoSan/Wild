import json
import math
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.player import Player
from player.views.get_subclasses import get_subclasses
from region.views.distance_counting import distance_counting
from storage.models.destroy import Destroy
from storage.models.storage import Storage
from storage.models.stock import Stock
from storage.models.good import Good
from storage.views.storage.check_cap_exists import check_cap_exists
from storage.views.storage.check_goods_exists import check_goods_exists
from storage.views.storage.get_transfer_price import get_transfer_price
from storage.views.storage.transfer_values import transfer_values
from war.models.wars.war import War
from region.views.find_route import find_route


# передача товаров между Складами
@login_required(login_url='/')
@check_player
@transaction.atomic
def assets_transfer(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        # получаем целевой склад
        dest_pk = request.POST.get('dest_storage')

        if not dest_pk or dest_pk == 'null':
            data = {
                'response': pgettext('assets', 'Целевой Склад не заполнен'),
                'header': pgettext('assets', 'Перемещение товаров'),
                'grey_btn': pgettext('assets', 'Закрыть'),
            }
            return JsonResponse(data)

        try:
            dest_pk_int = int(dest_pk)

        except ValueError:
            return {
                'header': pgettext('assets', 'Перемещение товаров'),
                'grey_btn': pgettext('assets', 'Закрыть'),
                'response': pgettext('assets', 'Целевой Склад должен быть целым числом'),
            }

        # проверяем, есть ли целевой склад среди складов игрока
        storages = Storage.actual.filter(owner=player)
        storages_pk = []
        # словарь склад - словарь стоимости до других регионов со складами, как в assets.py
        trans_mul = {}

        for storage in storages:
            storages_pk.append(storage.pk)

            trans_mul[storage.pk] = {}
            for dest in storages:
                if not dest == storage:
                    # trans_mul[storage.pk][dest.pk] = math.ceil(distance_counting(storage.region, dest.region) / 100)
                    path, trans_mul[storage.pk][dest.pk] = find_route(storage.region, dest.region)

        if dest_pk_int in storages_pk:

            iv_storages_pk = []
            storages_values = json.loads(request.POST.get('storages'))
            # проверяем, что все склады принадлежат игроку
            for i_storg in storages_values.keys():
                if len(storages_values.get(i_storg)):
                    iv_storages_pk.append(int(i_storg))

                if not int(i_storg) in storages_pk:
                    data = {
                        'response': str(pgettext('assets', 'Склад')) + ' ' + i_storg + ' ' + str(pgettext('assets',
                                                                                                 'вам не принадлежит')),
                        'header': pgettext('assets', 'Перемещение товара'),
                        'grey_btn': pgettext('assets', 'Закрыть'),
                    }
                    return JsonResponse(data)

            sources_reg = []
            for sources_pk in iv_storages_pk:
                if storages.get(pk=sources_pk).region not in sources_reg:
                    sources_reg.append(storages.get(pk=sources_pk).region)

            # классы всех типов войн
            war_classes = get_subclasses(War)
            for war_cl in war_classes:
                # исключение - тест войны
                if war_cl.__name__ == 'EventWar':
                    continue
                # если есть войны за этот рег
                if war_cl.objects.filter(running=True, def_region__in=sources_reg).exists():
                    data = {
                        'response': pgettext('assets', 'Запрещено вывозить товары из атакованных регионов'),
                        'header': pgettext('assets', 'Перемещение товара'),
                        'grey_btn': pgettext('assets', 'Закрыть'),
                    }
                    return JsonResponse(data)

            # список айдишников запасов, которые будем обрабатывать
            stocks_pk_list = []
            # идем по всем складам
            for storage_pk in storages_values.keys():
                # если в текущем Складе есть ресурсы
                if len(storages_values.get(storage_pk)):
                    # идем по списку запасов
                    for stock_pk in storages_values.get(storage_pk):
                        # собираем айдишники запасов
                        stocks_pk_list.append(int(stock_pk))
            # получаем
            stocks = Stock.objects.filter(pk__in=stocks_pk_list).only('pk', 'storage__id')
            # список айдишников запасов, которые найдены
            stocks_pk_found = []

            for stock in stocks:
                if stock.storage.id not in storages_pk:
                    data = {
                        'response': pgettext('assets', 'Один или несколько запасов не принадлежат вашим складам'),
                        'header': pgettext('assets', 'Перемещение товара'),
                        'grey_btn': pgettext('assets', 'Закрыть'),
                    }
                    return JsonResponse(data)

                stocks_pk_found.append(stock.pk)

            if not set(stocks_pk_list).issubset(set(stocks_pk_found)):
                data = {
                    'response': pgettext('assets', 'Один или несколько запасов не существуют'),
                    'header': pgettext('assets', 'Перемещение товара'),
                    'grey_btn': pgettext('assets', 'Закрыть'),
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
                        status, size_type, sent, exist_cap = check_cap_exists(Storage.actual.get(pk=dest_pk_int),
                                                                         storages_values)

                        if status:
                            # потом убедиться, что у игрока есть деньги, оплатить передачу ресурсов
                            price, prices = get_transfer_price(trans_mul, dest_pk_int, storages_values)
                            if player.cash >= price:
                                # логируем
                                CashLog.create(player=player, cash=0 - price, activity_txt='trans')
                                # оплата
                                player.cash -= price
                                player.save()
                                # передача ресурсов
                                transfer_values(Storage.actual.get(pk=dest_pk_int), storages_values, prices)

                            else:
                                data = {
                                    'response': pgettext('assets', 'Недостаточно средств для оплаты доставки'),
                                    'header': pgettext('assets', 'Перемещение товара'),
                                    'grey_btn': pgettext('assets', 'Закрыть'),
                                }
                                return JsonResponse(data)
                        else:
                            data = {
                                'response': str(Storage.actual.get(pk=dest_pk_int).region.region_name) + ', '
                                            + str(size_type) + ' ' +  str(pgettext('assets', 'типоразмер:')) + ' ' +
                                            # ' ' +
                                            str(pgettext('assets', 'недостаточно места для товара.')) + ' ' +
                                            str(pgettext('assets', 'Требуется: ')) + str(sent) + str(pgettext('assets', ', в наличии: ')) + str(exist_cap),

                                'header': pgettext('assets', 'Перемещение товара'),
                                'grey_btn': pgettext('assets', 'Закрыть'),
                            }
                            return JsonResponse(data)
                    else:
                        data = {
                            'response': str(pgettext('assets', 'На складе в регионе ')) + str(ret_storg.region.region_name) +
                                        str(pgettext('assets', ' недостаточно товара ')) + good + str(pgettext('assets', ' для передачи.')) + '\n' +
                                        str(pgettext('assets', 'Требуется: ')) + str(required) + str(pgettext('assets',
                                                                                                     ', в наличии: ')) + str(
                                exist),
                            'header': pgettext('assets', 'Перемещение товара'),
                            'grey_btn': pgettext('assets', 'Закрыть'),
                        }
                        return JsonResponse(data)
                else:
                    data = {
                        'response': pgettext('assets', 'Товары для передачи не выбраны'),
                        'header': pgettext('assets', 'Перемещение товара'),
                        'grey_btn': pgettext('assets', 'Закрыть'),
                    }
                    return JsonResponse(data)
            else:
                data = {
                    'response': pgettext('assets', 'В целевом Складе заполнены значения'),
                    'header': pgettext('assets', 'Перемещение товара'),
                    'grey_btn': pgettext('assets', 'Закрыть'),
                }
                return JsonResponse(data)
        else:
            data = {
                'response': pgettext('assets', 'Целевой Склад вам не принадлежит'),
                'header': pgettext('assets', 'Перемещение товара'),
                'grey_btn': pgettext('assets', 'Закрыть'),
            }
            return JsonResponse(data)

        data = {
            'response': 'ok',
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'header': pgettext('assets', 'Операции с товарами'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': pgettext('mining', 'Ошибка метода'),
        }
        return JsonResponse(data)
