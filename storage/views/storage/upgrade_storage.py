import math
import json
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.player import Player
from region.views.distance_counting import distance_counting
from storage.models.storage import Storage
from storage.views.storage.get_transfer_price import get_transfer_price
from django.utils.translation import pgettext
from storage.templatetags.get_verbose import get_verbose
from storage.templatetags.check_up_limit import check_up_limit


# переименование партии
@login_required(login_url='/')
@check_player
@transaction.atomic
def upgrade_storage(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        # если у игрока в этом регионе есть Склад
        if not Storage.actual.filter(owner=player, region=player.region).exists():
            data = {
                'header': pgettext('storage_upgrade', 'Улучшение Склада'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('storage', 'В этом регионе нет Склада'),
            }
            return JsonResponse(data)

        storage = Storage.actual.get(owner=player, region=player.region)

        if storage.level >= 5:
            data = {
                'header': pgettext('storage_upgrade', 'Улучшение Склада'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('storage_upgrade', 'Уровень Склада - максимальный'),
            }
            return JsonResponse(data)

        for material in ['aluminium', 'steel']:
            if getattr(storage, material) < 500:
                data = {
                    'header': pgettext('storage_upgrade', 'Улучшение Склада'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('storage_upgrade', 'Недостаточно материала: ') + str(get_verbose(material)),
                }
                return JsonResponse(data)

        upgrades = json.loads(request.POST.get('upgrades'))

        sizes_filled = {
            'large': {
                'now': 0,
                'limit': 5
            },

            'medium': {
                'now': 0,
                'limit': 6
            },

            'small': {
                'now': 0,
                'limit': 5
            },
        }

        # проверяем, сколько полей можно улучшить
        for size in Storage.sizes:
            limited = 0
            for good in Storage.sizes[size]:
                # узнаем, поле в лимите или нет
                if check_up_limit(storage, good, size):
                    limited += 1
                    # если поле в лимите хотят прокачать
                    if upgrades[good] == 1:
                        data = {
                            'header': pgettext('storage_upgrade', 'Улучшение Склада'),
                            'grey_btn': pgettext('mining', 'Закрыть'),
                            'response': pgettext('storage_upgrade', 'Максимально улучшено: ') + str(get_verbose(good)),
                        }
                        return JsonResponse(data)

            # if limited == sizes_filled[size]['limit']:
            #     sizes_filled[size]['limit'] = 1

        for size in Storage.sizes:
            for good in Storage.sizes[size]:
                # если указан для прокачки
                if upgrades[good] == 1:
                    sizes_filled[size]['now'] += 1

                if sizes_filled[size]['now'] > sizes_filled[size]['limit']:
                    data = {
                        'header': pgettext('storage_upgrade', 'Улучшение Склада'),
                        'grey_btn': pgettext('mining', 'Закрыть'),
                        'response': pgettext('storage_upgrade', 'Превышение числа позиций для улучшения'),
                    }
                    return JsonResponse(data)

            if sizes_filled[size]['now'] < sizes_filled[size]['limit']:
                data = {
                    'header': pgettext('storage_upgrade', 'Улучшение Склада'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                    'response': pgettext('storage_upgrade', 'Указаны не все позиции для улучшения'),
                }
                return JsonResponse(data)

        mul = 1
        for size in Storage.sizes:
            if size == 'large':
                mul = 10000
            elif size == 'medium':
                mul = 1000
            elif size == 'small':
                mul = 100

            for good in Storage.sizes[size]:
                # если указан для прокачки
                if upgrades[good] == 1:
                    # если только построен
                    if getattr(storage, good + '_cap') / mul == 1:
                        setattr(storage, good + '_cap', getattr(storage, good + '_cap') + 1 * mul)
                    # если уже второго уровня
                    elif getattr(storage, good + '_cap') / mul == 2:
                        setattr(storage, good + '_cap', getattr(storage, good + '_cap') + 2 * mul)
                    # если уже третьего уровня
                    elif getattr(storage, good + '_cap') / mul == 4:
                        setattr(storage, good + '_cap', getattr(storage, good + '_cap') + 2 * mul)
                    # если уже третьего уровня
                    elif getattr(storage, good + '_cap') / mul == 6:
                        setattr(storage, good + '_cap', getattr(storage, good + '_cap') + 4 * mul)

        storage.level += 1
        storage.aluminium -= 500
        storage.steel -= 500
        storage.save()

        data = {
            'response': 'ok',
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'header': pgettext('storage', 'Передача денег'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': pgettext('mining', 'Ошибка метода'),
        }
        return JsonResponse(data)
