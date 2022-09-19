import json
from datetime import datetime
import random
import pytz
import redis
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.templatetags.static import static
from django.utils.translation import ugettext as _
from state.models.parliament.parliament_party import ParliamentParty
from state.models.parliament.parliament import Parliament
from chat.models.stickers_ownership import StickersOwnership
from chat.models.sticker import Sticker
from chat.models.sticker_pack import StickerPack
from gov.models.president import President
from gov.models.presidential_voting import PresidentialVoting
from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from polls.models.poll import Poll
from region.region import Region
from state.models.state import State
from wild_politics.settings import TIME_ZONE, sentry_environment
from region.views.lists.get_regions_online import get_region_online

# главная страница
@login_required(login_url='/')
@check_player
def overview(request):
    player = Player.get_instance(account=request.user)

    # регионы государства если они есть
    if player.region.state:
        regions_state = Region.objects.filter(state=player.region.state)
    else:
        regions_state = [player.region, ]

    # партии
    region_parties = Party.objects.filter(deleted=False, region=player.region).count()
    world_parties = Party.objects.filter(deleted=False).count()
    if player.region.state:
        state_parties = Party.objects.filter(region__in=regions_state, deleted=False).count()
    else:
        state_parties = region_parties

    # население
    world_pop = Player.objects.all().count()

    # население и онлайн рега
    region_pop, region_online = get_region_online(player.region)

    # население и онлайн госа
    if player.region.state:
        state_pop = 0
        state_online = 0
        for st_region in regions_state:
            region_pop_t, region_online_t = get_region_online(st_region)
            state_pop += region_pop_t
            state_online += region_online_t
    else:
        state_pop = region_pop
        state_online = region_online

    # число стран
    world_states = State.actual.all().count()

    # партии
    has_parl = False
    p_parties_list = None
    if player.region.state:
        parties_list = Party.objects.filter(deleted=False, region__in=regions_state)
        # парламентские партии
        if Parliament.objects.filter(state=player.region.state).exists():
            has_parl = True
            p_parties_list = ParliamentParty.objects.filter(parliament=Parliament.objects.get(state=player.region.state))
    else:
        parties_list = Party.objects.filter(deleted=False, region=player.region)

    messages = []

    stickers_dict = {}
    stickers_header_dict = {}
    header_img_dict = {}

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

        for sticker_own in stickers:
            # название пака
            stickers_header_dict[sticker_own.pack.pk] = sticker_own.pack.title
            #  получим рандомную картинку для заголовка
            header_img_dict[sticker_own.pack.pk] = random.choice(Sticker.objects.filter(pack=sticker_own.pack)).image.url
            # все остальные картинки - в словарь
            stickers_dict[sticker_own.pack.pk] = Sticker.objects.filter(pack=sticker_own.pack)

    http_use = False
    if sentry_environment == "development":
        http_use = True

    # polls = Poll.actual.all()

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
    if 'redesign' not in groups:
        page = 'player/redesign/overview.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': _('Обзор'),

        'player': player,

        'region_parties': region_parties,
        'world_parties': world_parties,
        'state_parties': state_parties,

        'world_pop': world_pop,

        'state_pop': state_pop,
        'state_online': state_online,

        'region_pop': region_pop,
        'region_online': region_online,

        'world_states': world_states,

        'regions_count': Region.objects.all().count(),
        'world_free': Region.objects.filter(state=None).count(),

        'parties_list': parties_list,
        'has_parl': has_parl,
        'p_parties_list': p_parties_list,

        'messages': messages,

        'stickers_header_dict': stickers_header_dict,
        'header_img_dict': header_img_dict,
        'stickers_dict': stickers_dict,

        'http_use': http_use,

        # 'polls': polls,

        'has_voting': has_voting,
        'president': president_post,

    })

    # r.flushdb()

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
