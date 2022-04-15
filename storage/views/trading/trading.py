from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404

from player.decorators.player import check_player
from player.player import Player
from storage.models.storage import Storage
from storage.models.transport import Transport


@login_required(login_url='/')
@check_player
# открытие страницы торговли
def trading(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    return render(request, 'storage/trading/trading.html', {'player': player,
                                                            'storage_cl': Storage,
                                                            'transport': Transport,
                                                            })
