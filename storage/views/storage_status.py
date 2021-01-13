from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils.translation import ugettext as _

from player.player import Player
from storage.models.storage import Storage
from player.decorators.player import check_player


# возвращает состояние склада на данный момент
@login_required(login_url='/')
@check_player
def storage_status(request, pk):
    if request.method == "GET":
        # получаем персонажа
        player = Player.objects.get(account=request.user)
        data = {}
        if pk == '0':
            data = {
                'gold': player.gold,
                'cash': player.cash,
                'storage_cash': Storage.objects.get(owner=player, region=player.region).cash,
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
                    'header': _('Energy recharging'),
                    'response': _('no_batteries'),
                    'grey_btn': _('Close'),
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
            data['responce'] = _('not_correct')

        return JsonResponse(data)
    else:
        return HttpResponse('no', content_type='text/html')
