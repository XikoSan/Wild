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

        int_pk = None
        try:
            int_pk = int(pk)

        except ValueError:
            pass

        # если передан числовой параметр
        if int_pk is not None:
            # пользовательские данные
            if pk == '0':
                storage_cash = 0
                if Storage.actual.filter(owner=player, region=player.region).exists():
                    storage_cash = Storage.actual.get(owner=player, region=player.region).cash
                data = {
                    'gold': player.gold,
                    'cash': player.cash,
                    'storage_cash': storage_cash,
                    'locked': locked,
                    'bottles': player.bottles,
                    'energy': player.energy
                }
            # конкретный склад
            else:
                if Storage.actual.filter(pk=int_pk, owner=player).exists():
                    data = Storage.actual.get(pk=int_pk, owner=player).allStorageCount()

                else:
                    data = {
                        'mode': 'notify',
                        'response': 'Склад с указанным ID не существует или не принадлежит вам',
                        'header': 'Данные склада',
                        'grey_btn': 'Закрыть',
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
            data = Storage.actual.get(owner=player, region=player.region).allStorageCount()
        # получаем ресурсы
        elif pk == 'resourses':
            data = Storage.actual.get(owner=player, region=player.region).unitsOnStorageCount('resourses')
        # получаем материалы
        elif pk == 'materials':
            data = Storage.actual.get(owner=player, region=player.region).unitsOnStorageCount('materials')
        # получаем юнитов
        elif pk == 'units':
            data = Storage.actual.get(owner=player, region=player.region).unitsOnStorageCount('units')
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
