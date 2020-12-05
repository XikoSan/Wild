# import operator
# from datetime import timedelta
# from django.conf import settings
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
# from django.db.models import Q
from django.shortcuts import redirect, render
# from django.utils import timezone, translation
# from django.utils.translation import ugettext as _
# from itertools import chain
#
# from gamecore.all_models.Party.party import Party
# from gamecore.all_models.events.event import GameEvent
# from gamecore.all_models.gov.parliament import Parliament, ParliamentVoting
# from gamecore.all_models.gov.state import State
# from gamecore.all_models.mail import Message
from player.player import Player
# from region.region import Region
# from gamecore.all_models.war.ground_war import GroundWar
# from gamecore.all_models.war.war import War
from player.decorators.player import check_player
# from gamecore.all_views.get_subclasses import get_subclasses
# from gamecore.all_views.header.until_recharge import IntervalInSeconds, UntilRecharge


# главная страница
@login_required(login_url='/')
@check_player
def mining(request):

    player = Player.objects.get(account=request.user)
    # отправляем в форму
    response = render(request, 'region/mining.html', {
        # 'page_name': _('Overview'),

        'player': player,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
