import json
from datetime import datetime

import pytz
import redis
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.templatetags.static import static
from django.utils.translation import ugettext as _
from gov.models.presidential_voting import PresidentialVoting
from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from polls.models.poll import Poll
from region.region import Region
from wild_politics.settings import TIME_ZONE, sentry_environment
from chat.models.stickers_ownership import StickersOwnership
from gov.models.president import President

# главная страница
@login_required(login_url='/')
@check_player
def overview(request):
    player = Player.objects.get(account=request.user)

    region_parties = Party.objects.filter(deleted=False, region=player.region).count()
    world_parties = Party.objects.filter(deleted=False).count()

    world_pop = Player.objects.all().count()
    region_pop = Player.objects.filter(region=player.region).count()
    state_pop = region_pop

    region_parties_list = Party.objects.filter(deleted=False, region=player.region)

    if player.region.state:
        reigions_state = Region.objects.filter(state=player.region.state)
        state_pop = Player.objects.filter(region__in=reigions_state).count()

    messages = []
    stickers = None

    if not player.chat_ban:
        r = redis.StrictRedis(host='redis', port=6379, db=0)

        counter = 0

        if r.hlen('counter') > 0:
            counter = r.hget('counter', 'counter')

        redis_list = r.zrangebyscore("chat", 0, counter, withscores=True)

        for scan in redis_list:
            b = json.loads(scan[0])

            if not Player.objects.filter(pk=int(b['author'])).exists():
                r.zremrangebyscore('chat', int(scan[1]), int(scan[1]))
                continue

            author = Player.objects.filter(pk=int(b['author'])).only('id', 'nickname', 'image', 'time_zone').get()
            # сначала делаем из наивного времени aware, потом задаем ЧП игрока
            b['dtime'] = datetime.fromtimestamp(int(b['dtime'])).replace(tzinfo=pytz.timezone(TIME_ZONE)).astimezone(
                tz=pytz.timezone(player.time_zone)).strftime("%H:%M")
            b['author'] = author.pk
            b['counter'] = int(scan[1])
            b['author_nickname'] = author.nickname
            if author.image:
                b['image_link'] = author.image.url
            else:
                b['image_link'] = static('img/nopic.png')

            messages.append(b)

        stickers = StickersOwnership.objects.filter(owner=player)

    http_use = False
    if sentry_environment == "development":
        http_use = True

    polls = Poll.actual.all()

    president_post = has_voting = None
    # если есть гос
    if player.region.state:
        # если в госе есть през
        if President.objects.filter(state=player.region.state).exists():
            president_post = President.objects.get(state=player.region.state)
            # если идут выборы президента
            if PresidentialVoting.objects.filter(running=True, president=president_post).exists():
                has_voting = True

    groups = list(player.account.groups.all().values_list('name', flat=True))
    page = 'player/overview.html'
    if 'redesign' in groups:
        page = 'player/redesign/overview.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': _('Обзор'),

        'player': player,
        'region_parties': region_parties,
        'world_parties': world_parties,

        'world_pop': world_pop,
        'state_pop': state_pop,
        'region_pop': region_pop,

        'regions_count': Region.objects.all().count(),

        'region_parties_list': region_parties_list,

        'messages': messages,
        'stickers': stickers,

        'http_use': http_use,

        'polls': polls,

        'has_voting': has_voting,
        'president': president_post,

    })

    # r.flushdb()

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
