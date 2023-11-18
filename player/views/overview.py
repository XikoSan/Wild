import datetime
import json
import os
import pytz
import random
import redis
import vk
from vk.exceptions import VkAPIError
from allauth.socialaccount.models import SocialAccount, SocialToken
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.templatetags.static import static
from django.utils import timezone
from django.utils.translation import ugettext as _

from chat.models.sticker import Sticker
from chat.models.stickers_ownership import StickersOwnership
from gov.models.president import President
from gov.models.presidential_voting import PresidentialVoting
from party.party import Party
from player.decorators.player import check_player
from player.game_event.game_event import GameEvent
from player.logs.donut_log import DonutLog
from player.logs.gold_log import GoldLog
from player.player import Player
from player.player_settings import PlayerSettings
from player.views.get_subclasses import get_subclasses
from player.views.timers import interval_in_seconds
from region.models.region import Region
from region.views.lists.get_regions_online import get_region_online
from state.models.parliament.parliament import Parliament
from state.models.parliament.parliament_party import ParliamentParty
from state.models.parliament.parliament_voting import ParliamentVoting
from state.models.state import State
from war.models.wars.war import War
from wild_politics.settings import TIME_ZONE
from player.views.old_server_reward import old_server_rewards


# главная страница
@login_required(login_url='/')
@check_player
def overview(request):
    player = Player.get_instance(account=request.user)
    wiki_hide = False

    if PlayerSettings.objects.filter(player=player).exists():
        wiki_hide = PlayerSettings.objects.get(player=player).wiki_hide

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

    all_regions = Region.objects.only('pk').all()
    # население
    world_pop = Player.objects.all().count()

    # мировой онлайн
    regions_pop_dict = {}
    regions_online_dict = {}

    world_online = 0
    for region in all_regions:
        regions_pop_dict[region], regions_online_dict[region], players_online = get_region_online(region)
        world_online += regions_online_dict[region]

    # население и онлайн рега
    region_pop = regions_pop_dict[player.region]
    region_online = regions_online_dict[player.region]

    # население и онлайн госа
    if player.region.state:
        state_pop = 0
        state_online = 0
        for st_region in regions_state:
            state_pop += regions_pop_dict[st_region]
            state_online += regions_online_dict[st_region]
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
            p_parties_list = ParliamentParty.objects.filter(
                parliament=Parliament.objects.get(state=player.region.state))
    else:
        parties_list = Party.objects.filter(deleted=False, region=player.region)

    messages = []

    stickers_dict = {}
    stickers_header_dict = {}
    header_img_dict = {}

    r = None

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
            b['dtime'] = datetime.datetime.fromtimestamp(int(b['dtime'])).astimezone(
                tz=pytz.timezone(player.time_zone)).strftime("%H:%M")
            b['author'] = author.pk
            b['counter'] = int(scan[1])

            if len(author.nickname) > 25:
                b['author_nickname'] = f'{author.nickname[:25]}...'
            else:
                b['author_nickname'] = author.nickname

            if author.image:
                b['image_link'] = author.image.url
            else:
                b['image_link'] = 'nopic'

            b['user_pic'] = False
            # если сообщение - ссылка на изображение
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif']

            if any(extension in b['content'].lower() for extension in image_extensions):
                b['user_pic'] = True

            messages.append(b)

        stickers = StickersOwnership.objects.filter(owner=player)

        for sticker_own in stickers:
            # название пака
            stickers_header_dict[sticker_own.pack.pk] = sticker_own.pack.title
            #  получим рандомную картинку для заголовка
            header_img_dict[sticker_own.pack.pk] = random.choice(
                Sticker.objects.filter(pack=sticker_own.pack)).image.url
            # все остальные картинки - в словарь
            stickers_dict[sticker_own.pack.pk] = Sticker.objects.filter(pack=sticker_own.pack)

    http_use = False
    if os.getenv('HTTP_USE'):
        http_use = True

    # polls = Poll.actual.all()

    president_post = parliament = has_voting = has_parl_voting = None
    # если есть гос
    if player.region.state:
        # если в госе есть през
        if President.objects.filter(state=player.region.state).exists():
            president_post = President.objects.get(state=player.region.state)
            # если идут выборы президента
            if PresidentialVoting.objects.filter(running=True, president=president_post).exists():
                has_voting = True

        # если у государства есть парламент
        if Parliament.objects.filter(state=player.region.state).exists():
            parliament = Parliament.objects.get(state=player.region.state)

            # если в парламенте идут выборы
            if ParliamentVoting.objects.filter(running=True, parliament=parliament).exists():
                has_parl_voting = True

    has_event = None
    if GameEvent.objects.filter(running=True, event_start__lt=timezone.now(), event_end__gt=timezone.now()).exists():
        has_event = GameEvent.objects.get(running=True, event_start__lt=timezone.now(), event_end__gt=timezone.now())

    # войны
    war_dict = {}
    war_types = get_subclasses(War)

    for type in war_types:
        # если есть активные войны этого типа
        if type.objects.filter(running=True, deleted=False).exists():
            war_dict[type.__name__] = type.objects.filter(running=True, deleted=False).order_by('start_time').first()

    # находим войну, которая закончится раньше всех
    closest_war = None
    war_countdown = 0
    agr_damage = 0
    def_damage = 0

    for w_type in war_dict.keys():
        if not closest_war:
            closest_war = war_dict[w_type]
        else:
            if closest_war.start_time > war_dict[w_type].start_time:
                closest_war = war_dict[w_type]

    if closest_war:

        if not r:
            r = redis.StrictRedis(host='redis', port=6379, db=0)

        agr_damage = r.hget(f'{closest_war.__class__.__name__}_{closest_war.pk}_dmg', 'agr')
        if not agr_damage:
            agr_damage = 0
        else:
            agr_damage = int(agr_damage)

        def_damage = r.hget(f'{closest_war.__class__.__name__}_{closest_war.pk}_dmg', 'def')
        if not def_damage:
            def_damage = 0
        else:
            def_damage = int(def_damage)

        war_countdown = interval_in_seconds(
            object=closest_war,
            start_fname='start_time',
            end_fname=None,
            delay_in_sec=86400
        )

    player, reward_message = old_server_rewards(player)

    from metrics.models.daily_ore import DailyOre
    from metrics.models.daily_oil import DailyOil
    from django.db.models import Q
    from datetime import timedelta
    from player.logs.print_log import log
    from django.db.models import Sum

    if player.nickname == 'Администратор':

        # подбиваем недельные итоги
        if timezone.now().weekday() == 5:
            # берем сумму всех руд за прошедшую неделю
            date_now = timezone.now()
            date_7d = timezone.now() - timedelta(days=7)
            week_ore = DailyOre.objects.filter(Q(date__gt=date_7d), Q(date__lt=date_now)).aggregate(total_ore=Sum('ore'))['total_ore']
            # берем сумму всех марок нефти за прошедшую неделю
            week_oil = DailyOil.objects.filter(Q(date__gt=date_7d), Q(date__lt=date_now)).aggregate(total_oil=Sum('oil'))['total_oil']

            r = redis.StrictRedis(host='redis', port=6379, db=0)

            parties = Party.objects.only('pk', 'image', 'title').filter(deleted=False)

            mining_dict = {}

            for party in parties:
                if r.exists("party_mining_" + str(party.pk)):
                    mining_dict[party] = int(float(r.get("party_mining_" + str(party.pk))))

            sorted_items = sorted(mining_dict.items(), key=lambda x: x[1], reverse=True)[:10]

            # идем по каждой партии
            for party_tuple in sorted_items:
                if party_tuple[1] > 0:
                    # начисляем золото в процентном соотношении
                    log(f'добыча {party_tuple[0].title}: {int(20000 * (party_tuple[1] / (week_ore + week_oil)))}')

            # навыки
            all_skills = 0

            date_string = "2023-11-18"
            date = datetime.date.fromisoformat(date_string)

            log(timezone.now().date())
            log(date)

            if timezone.now().date() == date:
                for party in Party.objects.filter(deleted=False):
                    # берем сколько она добыла за неделю
                    if r.exists("party_skill_" + str(party.pk)):
                        all_skills += int(float(r.get("party_skill_" + str(party.pk))))
            else:
                if r.exists("all_skill"):
                    all_skills = int(float(r.get("all_skill")))
                    r.set("all_skill", 0)

            if r.exists("all_skill"):
                r.set("all_skill", 0)

            if all_skills > 0:

                mining_dict = {}

                for party in parties:
                    if r.exists("party_skill_" + str(party.pk)):
                        mining_dict[party] = int(float(r.get("party_skill_" + str(party.pk))))

                sorted_items = sorted(mining_dict.items(), key=lambda x: x[1], reverse=True)[:10]

                # идем по каждой партии
                for party_tuple in sorted_items:
                    # начисляем золото в процентном соотношении
                    if party_tuple[1] > 0:
                        # party.gold += 20000 * ( mined / (week_ore + week_oil) )
                        log(f'навыки {party_tuple[0].title}: {int(20000 * (party_tuple[1] / all_skills))}')

            # навыки
            all_produced = 0

            if timezone.now().date() == date:
                for party in Party.objects.filter(deleted=False):
                    # берем сколько она добыла за неделю
                    if r.exists("party_factory_" + str(party.pk)):
                        all_produced += int(float(r.get("party_factory_" + str(party.pk))))
            else:
                if r.exists("all_factory"):
                    all_produced = int(float(r.get("all_factory")))
                    r.set("all_factory", 0)

            if r.exists("all_factory"):
                r.set("all_factory", 0)

            if all_produced > 0:

                mining_dict = {}

                for party in parties:
                    if r.exists("party_factory_" + str(party.pk)):
                        mining_dict[party] = int(float(r.get("party_factory_" + str(party.pk))))

                sorted_items = sorted(mining_dict.items(), key=lambda x: x[1], reverse=True)[:10]

                # идем по каждой партии
                for party_tuple in sorted_items:
                    # начисляем золото в процентном соотношении
                    if party_tuple[1] > 0:
                        # party.gold += 20000 * ( mined / (week_ore + week_oil) )
                        log(f'навыки {party_tuple[0].title}: {int(20000 * (party_tuple[1] / all_produced))}')


    # call_donut_message = False
    #
    # if SocialToken.objects.filter(account__user=player.account, account__provider='vk').exists():
    #     session = vk.Session(
    #         access_token=SocialToken.objects.get(account__user=player.account, account__provider='vk'))
    #     vk_api = vk.API(session)
    #
    #     from player.logs.print_log import log
    #
    #     try:
    #         # проверяем, что подписка вообще есть
    #         if vk_api.donut.isDon(
    #                 owner_id="-164930433",
    #                 v='5.131',
    #         ) == 1:
    #
    #             response = vk_api.donut.getSubscription(
    #                 owner_id="-164930433",
    #                 v='5.131',
    #             )
    #
    #             # если за последний месяц не было логов наград
    #             if not DonutLog.objects.filter(
    #                     player=player,
    #                     dtime__gte=datetime.datetime.now() - relativedelta(months=1)
    #             ).exists():
    #
    #                 # время, к которому прибавляем месяц
    #                 if player.premium > timezone.now():
    #                     from_time = player.premium
    #                 else:
    #                     from_time = timezone.now()
    #                 # наичисляем месяц према
    #                 player.premium = from_time + relativedelta(months=1)
    #
    #                 log = DonutLog(
    #                     player=player,
    #                     dtime=datetime.datetime.now()
    #                 )
    #                 log.save()
    #                 # начисляем золото на остаток доната
    #                 gold_sum = (int(response["amount"]) - 40) * 30
    #
    #                 player.gold += gold_sum
    #
    #                 gold_log = GoldLog(player=player, gold=gold_sum, activity_txt='donut')
    #                 gold_log.save()
    #
    #                 player.save()
    #                 call_donut_message = True
    #
    #     except VkAPIError as e:
    #         pass

    assistant_name = ('Ann', 'Анна')

    if not player.educated:
        assistant_name = random.choice([('Ann', 'Анна'), ('Lin', 'Лин'),  ('Maria', 'Мария'), ('Sofia', 'София'), ('Olga', 'Ольга')])

    page = 'player/redesign/overview.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': _('Обзор'),

        'player': player,
        'wiki_hide': wiki_hide,

        'region_parties': region_parties,
        'world_parties': world_parties,
        'state_parties': state_parties,

        'world_pop': world_pop,
        'world_online': world_online,

        'state_pop': state_pop,
        'state_online': state_online,

        'region_pop': region_pop,
        'region_online': region_online,

        'world_states': world_states,

        'regions_count': all_regions.count(),
        'world_free': Region.objects.filter(state=None).count(),

        'parties_list': parties_list,
        'has_parl': has_parl,
        'p_parties_list': p_parties_list,

        'messages': messages,

        'stickers_header_dict': stickers_header_dict,
        'header_img_dict': header_img_dict,
        'stickers_dict': stickers_dict,

        'http_use': http_use,

        'war': closest_war,
        'war_delta': def_damage - agr_damage,
        'war_countdown': war_countdown,

        # 'polls': polls,

        'has_voting': has_voting,
        'president': president_post,

        'has_parl_voting': has_parl_voting,
        'parliament': parliament,

        'has_event': has_event,

        'assistant_name': assistant_name,

        'reward_message': reward_message,
    })

    # r.flushdb()

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
