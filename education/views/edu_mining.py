import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player


# главная страница
@login_required(login_url='/')
@check_player
def edu_mining(request):
    player = Player.get_instance(account=request.user)

    if player.educated:  # Замените `условие` на вашу проверку
        from django.shortcuts import redirect
        return redirect('overview')  # Перенаправляет на другую страницу при невыполнении условия

    page = 'education/edu_mining.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('education', 'Добыча'),
        'player': player,
    })
    return response
