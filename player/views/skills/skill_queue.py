import json
from datetime import datetime

import pytz
import redis
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.templatetags.static import static
from django.utils.translation import ugettext as _

from chat.models.stickers_ownership import StickersOwnership
from gov.models.president import President
from gov.models.presidential_voting import PresidentialVoting
from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from polls.models.poll import Poll
from region.region import Region
from wild_politics.settings import TIME_ZONE, sentry_environment


# главная страница
@login_required(login_url='/')
@check_player
def skill_queue(request):
    player = Player.get_instance(account=request.user)

    # отправляем в форму
    return render(request, 'player/skills/skill_queue.html', {
        'page_name': _('Навыки'),

        'player': player,

    })
