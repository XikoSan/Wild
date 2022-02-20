from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse

from player.decorators.player import check_player
from player.logs.gold_log import GoldLog
from player.player import Player


# переименование партии
@login_required(login_url='/')
@check_player
@transaction.atomic
def produce_energy(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.get(account=request.user)

        try:
            count = int(request.POST.get('energy_field', ''))

        except ValueError:
            return {
                'header': 'Ошибка производства энергии',
                'grey_btn': 'Закрыть',
                'response': 'Введите целое число',
            }

        if not count % 10 == 0:
            data = {
                'response': 'Введите число, кратное десяти',
                'header': 'Ошибка производства энергии',
                'grey_btn': 'Закрыть',
            }
            return JsonResponse(data)

        if not int(count) > 0:
            data = {
                'response': 'Введите положительное число',
                'header': 'Ошибка производства энергии',
                'grey_btn': 'Закрыть',
            }
            return JsonResponse(data)

        if player.gold >= int(count) / 10:
            player.gold -= int(count) / 10

            gold_log = GoldLog(player=player, gold=0 - (int(count) / 10), activity_txt='energy')
            gold_log.save()

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
                'header': 'Ошибка производства энергии',
                'grey_btn': 'Закрыть',
            }
            return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': 'Ты уверен что тебе сюда, путник?',
            'header': 'Ошибка производства энергии',
            'grey_btn': 'Закрыть',
        }
        return JsonResponse(data)
