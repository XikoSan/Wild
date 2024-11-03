import datetime
import pytz
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.translation import ugettext as _
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.logs.auto_mining import AutoMining
from player.player import Player
from region.models.fossils import Fossils
from skill.models.excavation import Excavation
from skill.models.fracturing import Fracturing
from state.models.state import State
from region.building.defences import Defences
from region.building.hospital import Hospital

# главная страница
@login_required(login_url='/')
@check_player
def mining(request):
    player = Player.get_instance(account=request.user)

    premium = False

    if player.premium > timezone.now():
        premium = True

    auto_mining = None

    if AutoMining.objects.filter(player=player).exists():
        auto_mining = AutoMining.objects.get(player=player)

        if not premium:
            auto_mining.delete()
            auto_mining = None

    pwr_earn = player.calculate_earnings(player.power)
    int_earn = player.calculate_earnings(player.knowledge)
    end_earn = player.calculate_earnings(player.endurance)

    daily_limit = 20000 + pwr_earn + int_earn + end_earn

    # ------------------

    CashEvent = apps.get_model('event.CashEvent')
    bonus = 0

    if CashEvent.objects.filter(running=True, event_start__lt=timezone.now(),
                                event_end__gt=timezone.now()).exists():

        event = CashEvent.objects.get(running=True, event_start__lt=timezone.now(),
                                      event_end__gt=timezone.now())

        cursor = connection.cursor()

        cursor.execute(
            f'SELECT event_invite.sender_id,SUM(player_player.endurance+player_player.knowledge+player_player.power-event_invite.exp)*2 AS total_stats FROM public.event_invite INNER JOIN public.player_player ON event_invite.invited_id=player_player.id WHERE sender_id = {player.pk} and event_id = {event.id} GROUP BY event_invite.sender_id ORDER BY total_stats DESC limit 1;')

        raw_top = cursor.fetchall()

        if raw_top:
            bonus = raw_top[0][1] // 10

    if bonus > 0:
        daily_limit = int(daily_limit * (1 + (bonus / 100)))

    # ------------------

    GameEvent = apps.get_model('player.GameEvent')
    EventPart = apps.get_model('player.EventPart')
    bonus = 0

    if GameEvent.objects.filter(running=True, event_start__lt=timezone.now(),
                                event_end__gt=timezone.now()).exists():
        event = GameEvent.objects.get(running=True, event_start__lt=timezone.now(), event_end__gt=timezone.now())

        if EventPart.objects.filter(player=player, event=event).exists():
            bonus = EventPart.objects.get(player=player, event=event).boost

    if bonus > 0:
        daily_limit = int(daily_limit * (1 + (bonus / 100)))

    # ------------------
    paid_sum = player.paid_sum
    # бонус по выходным
    if timezone.now().date().weekday() == 5 or timezone.now().date().weekday() == 6:
        daily_limit = daily_limit * 2
        paid_sum = paid_sum * 2

    # 3500 - количество энергии, которую надо выфармить за день
    if player.paid_consumption >= player.energy_limit:
        daily_procent = 100
    else:
        daily_procent = player.energy_consumption / ((player.energy_limit - player.paid_consumption) / 100)

    if daily_procent > 100:
        daily_procent = 100

    # сумма, которую уже можно забрать
    daily_current_sum = int((daily_limit - paid_sum) / 100 * daily_procent)

    daily_energy_limit = 0
    if player.energy_limit - player.paid_consumption > 0:
        daily_energy_limit = player.energy_limit - player.paid_consumption

    oil_mark = 'WTI'
    for type in player.region.oil_types:
        if type in player.region.oil_mark.name:
            oil_mark = type

    # --------------------

    fossils = Fossils.objects.filter(region=player.region).order_by('-good__name_ru')

    be_mined_dict = {}

    for mineral in fossils:
        # облагаем налогом добытую руду
        total_ore = (1 / 50) * mineral.percent * (1 + player.endurance * 0.01)
        # экскавация
        if Excavation.objects.filter(player=player, level__gt=0).exists():
            total_ore = Excavation.objects.get(player=player).apply({'sum': total_ore})

        if not player.account.date_joined + datetime.timedelta(days=7) > timezone.now():
            taxed_ore = State.get_taxes(player.region, total_ore, 'ore', mineral.good)
        else:
            taxed_ore = total_ore

        be_mined_dict[mineral] = taxed_ore

    # облагаем налогом добытую нефть
    total_oil = (1 / 10) * 20 * (1 + player.endurance * 0.01)

    # гидроразрыв
    if Fracturing.objects.filter(player=player, level__gt=0).exists():
        total_oil = Fracturing.objects.get(player=player).apply({'sum': total_oil})

    if not player.account.date_joined + datetime.timedelta(days=7) > timezone.now():
        taxed_oil = State.get_taxes(player.region, total_oil, 'oil', player.region.oil_mark)
    else:
        taxed_oil = total_oil

    be_mined_dict['oil'] = taxed_oil

    # --------------------

    defences_level = 0

    if not player.region.state:
        if Defences.objects.filter(region=player.region, level__gt=0).exists():
            defences_level = Defences.objects.get(region=player.region).level

    hospital_level = 0

    if not player.region.state:
        if Hospital.objects.filter(region=player.region, level__gt=0).exists():
            hospital_level = Hospital.objects.get(region=player.region).level


    groups = list(player.account.groups.all().values_list('name', flat=True))
    page = 'region/mining.html'
    if 'redesign' not in groups:
        page = 'region/redesign/mining.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name':pgettext('mining', 'Добыча'),

        'player': player,
        'premium': premium,
        'auto_mining': auto_mining,

        'daily_limit': daily_limit,
        'daily_energy_limit': daily_energy_limit,
        'daily_procent': daily_procent,
        'daily_current_sum': daily_current_sum,

        'be_mined_dict': be_mined_dict,

        'oil_mark': oil_mark,
        'fossils': fossils,

        'defences_level': defences_level,
        'hospital_level': hospital_level,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
