from django.contrib.auth.decorators import login_required
from django.db import connection
from django.shortcuts import redirect, render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from player.views.lists.get_thing_page import get_thing_page
from region.models.region import Region


# список людей с самыми прокаченными навыками
# page - открываемая страница
@login_required(login_url='/')
@check_player
def parties_top(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # отправляем в форму
    return render(request, 'party/redesign/lists/party_top.html', {
        'page_name': pgettext('party_top', 'Топ партий'),

        'player': player,
    })
