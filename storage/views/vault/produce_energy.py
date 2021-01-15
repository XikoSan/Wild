from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect

from player.decorators.player import check_player
from player.player import Player


# переименование партии
@login_required(login_url='/')
@check_player
@transaction.atomic
def produce_energy(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.get(account=request.user)

        count = request.POST.get('energy', '')

        if not int(count) % 10 == 0:
            data = {
                'response': 'Введите число, кратное десяти',
            }
            return JsonResponse(data)

        if not int(count) > 0:
            data = {
                'response': 'Введите положительное число',
            }
            return JsonResponse(data)

        if player.gold >= int(count) / 10:
            player.gold -= int(count) / 10
            player.bottles += int(count)
            player.save()
            data = {
                'response': 'ok',
                'gold': player.gold,
                'bottles': player.bottles,
            }
            return JsonResponse(data)
        else:
            data = {
                'response': 'Недостаточно средств',
            }
            return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': 'Ты уверен что тебе сюда, путник?',
        }
        return JsonResponse(data)
