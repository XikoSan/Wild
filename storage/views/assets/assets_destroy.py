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
from storage.views.storage.destroy_values import destroy_values
from war.models.wars.war import War


# уничтожение товаров
@login_required(login_url='/')
@check_player
@transaction.atomic
def assets_destroy(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        # проверяем, есть ли целевой склад среди складов игрока
        storages = Storage.actual.filter(owner=player)
        storages_pk = []

        for storage in storages:
            storages_pk.append(storage.pk)

        iv_storages_pk = []
        storages_values = json.loads(request.POST.get('storages'))
        # проверяем, что все склады принадлежат игроку
        for i_storg in storages_values.keys():
            if len(storages_values.get(i_storg)):
                iv_storages_pk.append(int(i_storg))

            if not int(i_storg) in storages_pk:
                data = {
                    'response': pgettext('assets', 'Склад') + ' ' + i_storg + ' ' + pgettext('assets',
                                                                                             'вам не принадлежит'),
                    'header': pgettext('assets', 'Уничтожение товара'),
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
                    'header': pgettext('assets', 'Уничтожение товара'),
                    'grey_btn': pgettext('assets', 'Закрыть'),
                }
                return JsonResponse(data)

            stocks_pk_found.append(stock.pk)

        if not set(stocks_pk_list).issubset(set(stocks_pk_found)):
            data = {
                'response': pgettext('assets', 'Один или несколько запасов не существуют'),
                'header': pgettext('assets', 'Уничтожение товара'),
                'grey_btn': pgettext('assets', 'Закрыть'),
            }
            return JsonResponse(data)

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

                # уничтожение ресурсов
                destroy_values(player, storages_values)

            else:
                data = {
                    'response': pgettext('assets', 'На складе в регионе ') + str(ret_storg.region.region_name) +
                                pgettext('assets', ' недостаточно товара ') + good + '.\n' +
                                pgettext('assets', 'Требуется: ') + str(required) + pgettext('assets',
                                                                                             ', в наличии: ') + str(
                        exist),
                    'header': pgettext('assets', 'Уничтожение товара'),
                    'grey_btn': pgettext('assets', 'Закрыть'),
                }
                return JsonResponse(data)
        else:
            data = {
                'response': pgettext('assets', 'Товары не выбраны'),
                'header': pgettext('assets', 'Уничтожение товара'),
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
            'grey_btn': pgettext('core', 'Закрыть'),
            'response': pgettext('core', 'Ошибка метода'),
        }
        return JsonResponse(data)
