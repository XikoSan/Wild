import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player

# главная страница
@login_required(login_url='/')
@check_player
def edu_election(request):
    player = Player.get_instance(account=request.user)

    page = 'education/edu_election.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('education', 'Выборы'),
        'player': player,
    })
    return response
