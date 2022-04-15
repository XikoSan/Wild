from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils.translation import ugettext as _
from django.db.models import Sum
from player.player import Player
from storage.models.storage import Storage
from player.decorators.player import check_player
from storage.models.cash_lock import CashLock
from wild_politics.settings import JResponse


# возвращает состояние склада на данный момент
@login_required(login_url='/')
@check_player
def storage_status(request, pk):
    if request.method == "GET":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        locked = 0
        locked_tmp = CashLock.objects.filter(lock_player=player, deleted=False).aggregate(total_cash=Sum('lock_cash'))
        if locked_tmp['total_cash'] \
                and locked_tmp['total_cash'] > 0:
            locked = locked_tmp['total_cash']

        if pk == '0':
            storage_cash = 0
            if Storage.objects.filter(owner=player, region=player.region).exists():
                storage_cash = Storage.objects.get(owner=player, region=player.region).cash
            data = {
                'gold': player.gold,
                'cash': player.cash,
                'storage_cash': storage_cash,
                'locked': locked,
                'bottles': player.bottles,
                'energy': player.energy
            }
        # узнаем, получится ли пополнить запас энергии
        elif pk == 'recharge':
            if player.bottles >= 100 - player.energy:
                data = {
                    'response': 'ok',
                }
            else:
                data = {
                    'mode': 'notify',
                    'response': 'Недостаточно Энергетиков. Создайте их в Хранилище Склада',
                    'header': 'Пополнение энергии',
                    'grey_btn': 'Закрыть',
                }
        # получаем всё
        elif pk == 'all':
            data = Storage.objects.get(owner=player, region=player.region).allStorageCount()
        # получаем ресурсы
        elif pk == 'resourses':
            data = Storage.objects.get(owner=player, region=player.region).unitsOnStorageCount('resourses')
        # получаем материалы
        elif pk == 'materials':
            data = Storage.objects.get(owner=player, region=player.region).unitsOnStorageCount('materials')
        # получаем юнитов
        elif pk == 'units':
            data = Storage.objects.get(owner=player, region=player.region).unitsOnStorageCount('units')
        else:
            data = {
                'mode': 'notify',
                'response': 'Некорректный параметр',
                'header': 'Информация со Склада',
                'grey_btn': 'Закрыть',
            }

        return JResponse(data)
    else:
        return HttpResponse('no', content_type='text/html')
