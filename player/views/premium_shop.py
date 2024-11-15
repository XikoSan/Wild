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
# открытие страницы премиум магазина
def premium_shop(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # ---------------------
    suit_version = False
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    if "WildPoliticsApp" in user_agent:
        import re
        from player.logs.print_log import log
        match = re.search(r"WildPoliticsApp_(\d+\.\d+\.\d+)", user_agent)
        if match:
            if version.parse(match.group(1)) >= version.parse("1.5.3"):
                suit_version = True

    # ---------------------

    usages = FreebieUsage.objects.filter(player=player)

    usages_list = []

    for usage in usages:
        usages_list.append(usage.type)

    page = 'player/redesign/premium_shop.html'

    response = render(request, page, {
        'page_name': pgettext('shop', 'Премиум-магазин'),
        'usages_list': usages_list,
        'player': player,

        'version': suit_version,
    })

    return response
