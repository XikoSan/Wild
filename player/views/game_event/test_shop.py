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
from player.logs.test_log import TestLog
from player.player import Player
from player.logs.test_point_usage import TestPointUsage


@login_required(login_url='/')
@check_player
# открытие страницы магазина очков
def test_shop(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # ---------------------

    points = 0

    usages = TestPointUsage.objects.filter(player=player)

    usages_list = []

    for usage in usages:
        usages_list.append(usage.type)
        points += usage.count

    test_points = TestLog.objects.filter(player=player).count() - points

    # ---------------------

    page = 'player/redesign/game_event/test_shop.html'

    response = render(request, page, {
        'page_name': 'Награды за тестирование',

        'player': player,
        'test_points': test_points,
        'usages_list': usages_list,
    })

    return response
