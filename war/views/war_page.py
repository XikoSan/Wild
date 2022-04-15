from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from player.decorators.player import check_player
from player.player import Player
from player.views.get_subclasses import get_subclasses
from war.models.wars.war import War
from itertools import chain

# страница войн
@login_required(login_url='/')
@check_player
def war_page(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    wars_list = None

    war_types = get_subclasses(War)
    for type in war_types:
        # если есть активные войны этого типа
        if type.objects.filter(running=True, deleted=False).exists():
            # если лист партий из парламента не пустой
            if wars_list:
                # добавляем в список на вывод
                wars_list = list(chain(wars_list, type.objects.filter(running=True, deleted=False)))
            else:
                wars_list = type.objects.filter(running=True, deleted=False)

    # отправляем в форму
    return render(request, 'war/war_page.html', {
        # самого игрока
        'player': player,
        # список войн
        'wars_list': wars_list,

    })
