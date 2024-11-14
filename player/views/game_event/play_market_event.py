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
from django.utils import translation
from django.utils.translation import check_for_language

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
    PlayerSettings = apps.get_model('player.PlayerSettings')

    en_lang = False

    language = request.LANGUAGE_CODE
    if language != 'ru':
        en_lang = True
    else:
        if PlayerSettings.objects.filter(player=player).exists():
            player_settings = PlayerSettings.objects.get(player=player)
            if player_settings.language != 'ru':
                en_lang = True
        # ---------------------

    page = 'player/redesign/game_event/play_market_event.html'

    response = render(request, page, {
        'page_name': pgettext('event', 'Наступление на Google Play'),

        'player': player,
        'en_lang': en_lang,
    })

    return response
