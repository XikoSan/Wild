import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.translation import pgettext
from time import gmtime
from time import strftime
from wild_politics.settings import JResponse

from player.decorators.player import check_player
from player.player import Player
from storage.models.good import Good
from storage.models.stock import Stock
from storage.models.storage import Storage


@check_player
def assets_info(request, pk):
    if request.method == "GET":

        player = Player.get_instance(account=request.user)

        if Storage.actual.filter(pk=pk, owner=player).exists():

            size_dict = {}
            for size in Good.sizeChoices:
                size_dict[size[0]] = size[1]

            storage = Storage.actual.get(pk=pk)

            all_goods = Good.objects.all()

            stocks = Stock.objects.filter(storage=storage, stock__gt=0, good__in=all_goods)

            all_stocks = {}

            for good in all_goods:

                if stocks.filter(good=good).exists():

                    stock = stocks.get(good=good, stock__gt=0)

                    if good.size in all_stocks:
                        all_stocks[good.size].append(stock)
                    else:
                        all_stocks[good.size] = [stock, ]

            page = 'storage/redesign/assets_info.html'

            return render(request, page, {
                'all_stocks': all_stocks,
                'storage': storage,
                'size_dict': size_dict
            })

        else:
            data = {
                'response': pgettext('assets_info', 'Такого склада у вас нет'),
                'header': pgettext('assets_info', 'Получение склада'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('assets_info', 'Получение склада'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
