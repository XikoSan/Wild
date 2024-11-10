import datetime
import json
import os
import pytz
import random
import redis
import vk
from allauth.socialaccount.models import SocialAccount, SocialToken
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.templatetags.static import static
from django.utils import timezone
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _
from vk.exceptions import VkAPIError

from chat.models.sticker import Sticker
from chat.models.stickers_ownership import StickersOwnership
from event.models.enter_event.activity_event import ActivityEvent
from gov.models.president import President
from gov.models.presidential_voting import PresidentialVoting
from party.party import Party
from player.decorators.player import check_player
from player.game_event.game_event import GameEvent
from player.logs.donut_log import DonutLog
from player.logs.gold_log import GoldLog
from player.logs.test_log import TestLog
from player.player import Player
from player.player_settings import PlayerSettings
from player.views.get_subclasses import get_subclasses
from player.views.old_server_reward import old_server_rewards
from player.views.timers import interval_in_seconds
from region.models.map_shape import MapShape
from region.models.region import Region
from region.models.region import Region
from region.views.lists.get_regions_online import get_region_online
from state.models.parliament.parliament import Parliament
from state.models.parliament.parliament_party import ParliamentParty
from state.models.parliament.parliament_voting import ParliamentVoting
from state.models.state import State
from war.models.wars.war import War
from wild_politics.settings import TIME_ZONE


# страница склада
@login_required(login_url='/')
@check_player
def edu_storage(request):
    player = Player.get_instance(account=request.user)

    page = 'education/edu_storage.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('education', 'Склад'),
        'player': player,
    })
    return response
