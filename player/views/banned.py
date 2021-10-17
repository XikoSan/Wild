# coding=utf-8

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.player import Player


@login_required(login_url='/')
# открытие страницы персонажа игрока
def banned(request):
    char_list = {}
    # Если у игрока есть персонаж:
    if Player.objects.filter(account=request.user).exists():
        # Получаем его
        player = Player.objects.get(account=request.user)
        # Если игрок забанен:
        if player.banned:
            return render(request, 'player/banned.html', {
                # получаем его
                'player': player,
            })
        else:
            # Перекидываем игрока в Overview
            return redirect('overview')
    # Иначе:
    else:
        # Пусть идет создавать нового персонажа
        return redirect('char_new')
