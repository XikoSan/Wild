from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect

from player.decorators.player import check_player
from player.player import Player
from region.views.distance_counting import distance_counting
from storage.storage import Storage


# переименование партии
@login_required(login_url='/')
@check_player
@transaction.atomic
def new_storage(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.get(account=request.user)

        # находим Склад, с которого хотят списать материалы
        if not Storage.objects.filter(pk=int(request.POST.get('storage'))):
            data = {
                'response': 'Не найден Склад',
            }
            return JsonResponse(data)

        paid_storage = Storage.objects.get(pk=int(request.POST.get('storage')))
        # считаем стоиомость создания нового Склада
        # она равна 500 * количество Складов сейчас
        material_cost = 500 * Storage.objects.filter(owner=player).count()
        # если ресурсов недостаточно
        if not (getattr(paid_storage, 'steel') >= material_cost \
                and getattr(paid_storage, 'aluminium') >= material_cost):
            data = {
                'response': 'Недостаточно ресурсов',
            }
            return JsonResponse(data)

        # списываем ресурсы
        setattr(paid_storage, 'steel', getattr(paid_storage, 'steel') - material_cost)
        setattr(paid_storage, 'aluminium', getattr(paid_storage, 'aluminium') - material_cost)
        paid_storage.save()

        setattr(player, 'cash', getattr(player, 'cash') - round(distance_counting(player.region, paid_storage.region)))
        player.save()

        storage = Storage(owner=player, region=player.region)
        storage.save()
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
