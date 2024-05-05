# coding=utf-8

from django.shortcuts import redirect
from django.shortcuts import render
from player.player import Player
from django.contrib.auth.decorators import login_required
from player.decorators.player import check_player

@login_required(login_url='/')
@check_player
def bonus_code(request):

    code = request.GET.get('code', '')

    # Получаем объект персонажа, по его ключу
    # Текущий пользователь
    player = Player.get_instance(account=request.user)

    return render(request, 'player/redesign/bonus_code/bonus_code.html', {
        'page_name': 'Активировать бонус-код',
        'player': player,
        'code': code,
    })
