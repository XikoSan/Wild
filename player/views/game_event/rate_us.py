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
from packaging import version
from player.decorators.player import check_player
from player.logs.test_log import TestLog
from player.player import Player
from player.logs.freebie_usage import FreebieUsage
from django.utils.translation import pgettext

@login_required(login_url='/')
@check_player
# оценка приложения
def rate_us(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    used = FreebieUsage.objects.filter(player=player, type='rate_gold').exists()

    page = 'player/redesign/rate_us.html'

    response = render(request, page, {
        'page_name': pgettext('shop', 'Премиум-магазин'),
        'player': player,

        'used': used,
    })

    return response
