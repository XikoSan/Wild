from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404

from player.decorators.player import check_player
from player.player import Player
from storage.models.storage import Storage


@login_required(login_url='/')
@check_player
# открытие страницы торговли
def trading(request):
    # получаем персонажа
    player = Player.objects.get(account=request.user)

    # получаем объект склада данного игрока
    storage = None
    # если склад есть
    if Storage.objects.filter(owner=player, region=player.region).exists():
        storage = Storage.objects.get(owner=player, region=player.region)



    return render(request, 'storage/trading.html', {'player': player,
                                                    'storage_cl': Storage
                                                       })
