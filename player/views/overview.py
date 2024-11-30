import datetime
import json
import os
import pytz
import random
import redis
import vk
from django.apps import apps
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
from event.models.enter_event.activity_event import ActivityEvent
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
from player.logs.test_log import TestLog
from django.utils.translation import pgettext
from packaging import version
from google_play_scraper import app
from django.utils.translation import get_language

# главная страница
@login_required(login_url='/')
@check_player
def overview(request):
    player = Player.get_instance(account=request.user)
    wiki_hide = False

    # user_agent = request.META.get('HTTP_USER_AGENT', '')
    #
    # if "WildPoliticsApp" in user_agent:
    #     import re
    #     from player.logs.print_log import log
    #     match = re.search(r"WildPoliticsApp_(\d+\.\d+\.\d+)", user_agent)
    #     if match:
    #         version = match.group(1)
    #         log(version)

        # if TestLog.objects.filter(player=player).exists():
        #     tst_log = TestLog.objects.filter(player=player).order_by('-dtime').first()
        #
        #
        #     if tst_log.dtime < timezone.now() - datetime.timedelta(days=1):
        #         new_tst = TestLog(player=player)
        #         new_tst.save()
        #
        # else:
        #     new_tst = TestLog(player=player)
        #     new_tst.save()

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

        appendix = ''
        chat_id = get_language()

        if chat_id not in ['ru', 'be', 'uk', 'hy']:
            # appendix = f'_{chat_id}'
            appendix = f'_en'

        counter = 0

        if r.hlen('counter' + appendix) > 0:
            counter = r.hget('counter' + appendix, 'counter')

        redis_list = r.zrangebyscore("chat" + appendix, 0, counter, withscores=True)

        for scan in redis_list:
            b = json.loads(scan[0])

            if not Player.objects.filter(pk=int(b['author'])).exists():
                r.zremrangebyscore('chat' + appendix, int(scan[1]), int(scan[1]))
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
                b['image_link'] = author.image_75.url
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

    activity_event = None
    if ActivityEvent.objects.filter(running=True, event_start__lt=timezone.now(), event_end__gt=timezone.now()).exists():
        activity_event = ActivityEvent.objects.get(running=True, event_start__lt=timezone.now(), event_end__gt=timezone.now())

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
            agr_damage = int(float(agr_damage))

        def_damage = r.hget(f'{closest_war.__class__.__name__}_{closest_war.pk}_dmg', 'def')
        if not def_damage:
            def_damage = 0
        else:
            def_damage = int(float(def_damage))

        def_damage += closest_war.defence_points

        war_countdown = interval_in_seconds(
            object=closest_war,
            start_fname='start_time',
            end_fname=None,
            delay_in_sec=86400
        )

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



    # from storage.views.vault.avia_box.generate_rewards import generate_rewards
    #
    # from player.logs.print_log import log
    #
    # for attmpt in range(10):
    #     for loop in range(10):
    #         reward_sum = 0
    #         total_reward_sum = 0
    #         for iter in range(100):
    #             reward, rarity = generate_rewards(player)
    #
    #             if rarity == 'gold':
    #                 reward_sum += reward
    #                 total_reward_sum += reward
    #
    #             elif rarity == 'epic':
    #                 total_reward_sum += 5000
    #
    #             elif rarity == 'rare':
    #                 total_reward_sum += 1000
    #
    #             elif rarity == 'common':
    #                 total_reward_sum += 500
    #
    #         log(f'цикл {loop+1}, выпало золота: {reward_sum}, всего: {total_reward_sum}')
    #     log(f'-----------------------------')

    # from region.views.map.gold_index import form_development_top
    # form_development_top()

    # from region.views.find_route import find_route
    # from player.logs.print_log import log
    #
    # region_1 = Region.objects.get(pk=2)
    # region_2 = Region.objects.get(pk=54)
    # # excluded_regions = [Region.objects.get(id=40), Region.objects.get(id=5), Region.objects.get(id=17)]
    # excluded_regions = []
    #
    # path, total_distance = find_route(region_1, region_2, excluded_regions)
    # if path:
    #     log(" -> ".join([str(region) for region in path]))
    #     log(f"Стоимость: {total_distance} $")
    # else:
    #     log("Path not found")

    # =----------------------
    # проверка версии приложения

    # Укажите пакет вашего приложения
    package_name = 'com.fogonrog.wildpolitics'
    # инфо о приложении
    app_info = app(package_name)

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    need_update = False

    if "WildPoliticsApp" in user_agent:
        import re
        match = re.search(r"WildPoliticsApp_(\d+\.\d+\.\d+)", user_agent)
        if match:
            # if version.parse(match.group(1)) != version.parse('1.9.9'):
            if version.parse(match.group(1)) != version.parse(app_info['version']):
                need_update = True

    # проверка версии приложения
    # =----------------------

    from datetime import timedelta
    from django.db.models import Sum, F, FloatField, Case, When
    from django.utils.timezone import now
    from metrics.models.daily_gold_by_state import DailyGoldByState
    from math import ceil
    from gov.models.minister import Minister

    # 1. Определяем дату 7 дней назад
    seven_days_ago = now().date() - timedelta(days=7)

    # 2. Суммируем общее золото за последние 7 дней для всех стран
    total_gold_last_7_days = DailyGoldByState.objects.filter(
        date__gte=seven_days_ago,
        state__type='Presidential'  # Учитываем только президентские страны
    ).aggregate(total_gold=Sum('daily_gold'))['total_gold'] or 0

    # 3. Получаем данные по президентским странам и их процент от общей добычи
    states_with_percentages = DailyGoldByState.objects.filter(
        date__gte=seven_days_ago,
        state__type='Presidential'  # Учитываем только президентские страны
    ).values('state__pk').annotate(
        state_total=Sum('daily_gold'),
        percentage=Case(
            When(state_total=0, then=0.0),  # Если заработок нулевой
            default=F('state_total') / total_gold_last_7_days,  # Иначе вычисляем процент
            output_field=FloatField(),
        )
    )

    from player.logs.print_log import log

    # 4. Распределяем золото лидерам президентских государств
    for state_data in states_with_percentages:
        state_pk = state_data['state__pk']
        percentage = state_data['percentage'] or 0.0

        # Вычисляем бонус
        gold_bonus = ceil(15000 * percentage * 0.33)

        # Находим президента
        try:
            president = President.objects.get(state__pk=state_pk)
            leader = president.leader

            if leader:
                # Добавляем золото лидеру
                leader.gold = F('gold') + gold_bonus
                leader.save(update_fields=['gold'])
                log(f"Лидеру {leader} добавлено {gold_bonus} золота")

            else:
                log(f"У государства с pk={state_pk} нет лидера")

        except President.DoesNotExist:
            log(f"Президент для государства с pk={state_pk} не найден")

        # если есть министры
        if Minister.objects.filter(state__pk=state_pk).exists():
            # их треть золота делим на число министров
            minister_bonus = ceil(gold_bonus / Minister.objects.filter(state__pk=state_pk).count())

            # для каждого министра
            for minister in Minister.objects.filter(state__pk=state_pk):
                # если есть
                if minister.player:
                    # Добавляем золото министру
                    minister.player.gold = F('gold') + minister_bonus
                    minister.player.save(update_fields=['gold'])
                    log(f"Министру {minister.player} добавлено {minister_bonus} золота")

        if ParliamentParty.objects.filter(parliament__state__id=state_pk).exists():
            # для каждой парламентской партии
            for pparty in ParliamentParty.objects.filter(parliament__state__id=state_pk):
                # каждая партия получает пропорционально числу мест в парламенте
                pparty_bonus = ceil(gold_bonus * (pparty.seats/100))

                # Добавляем золото партии
                pparty.party.gold = F('gold') + pparty_bonus
                pparty.party.save(update_fields=['gold'])
                log(f"Партии {pparty.party} добавлено {pparty_bonus} золота")

    log(f"Общее золото за последние 7 дней: {total_gold_last_7_days}")
    log(states_with_percentages)

    # =----------------------

    assistant_name = ('Ann', pgettext('education', 'Анна'))

    if not player.educated:
        assistant_name = random.choice([('Ann', pgettext('education', 'Анна')), ('Lin', pgettext('education', 'Лин')),  ('Maria', pgettext('education', 'Мария')), ('Sofia', pgettext('education', 'София')), ('Olga', pgettext('education', 'Ольга'))])

    page = 'player/redesign/overview.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('overview', 'Обзор'),

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
        'activity_event': activity_event,

        'assistant_name': assistant_name,

        'need_update': need_update,
    })

    # r.flushdb()

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
