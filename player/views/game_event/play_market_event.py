import pytz
from PIL import Image
from allauth.socialaccount.models import SocialAccount
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Sum
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

from player.decorators.player import check_player
from player.player import Player
from django.utils.translation import pgettext


@login_required(login_url='/')
@check_player
# страничка события
def play_market_event(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # ---------------------

    page = 'player/redesign/game_event/play_market_event.html'

    response = render(request, page, {
        'page_name': pgettext('event', 'Наступление на Google Play'),

        'player': player,
    })

    return response
