from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from player.logs.auto_mining import AutoMining


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


    # лимит денег, доступный игроку
    power = player.power
    if power > 100:
        power = 100

    knowledge = player.knowledge
    if knowledge > 100:
        knowledge = 100

    endurance = player.endurance
    if endurance > 100:
        endurance = 100

    daily_limit = 15000 + (power * 100) + (knowledge * 100) + (endurance * 100)

    # 3500 - количество энергии, которую надо выфармить за день
    if player.paid_consumption >= player.energy_limit:
        daily_procent = 100
    else:
        daily_procent = player.energy_consumption / ((player.energy_limit - player.paid_consumption) / 100)

    if daily_procent > 100:
        daily_procent = 100

    # сумма, которую уже можно забрать
    daily_current_sum = int((daily_limit - player.paid_sum) / 100 * daily_procent)

    # бонус по выходным
    if timezone.now().date().weekday() == 5 or timezone.now().date().weekday() == 6:
        if daily_current_sum != 0:
            daily_current_sum += daily_current_sum

    daily_energy_limit = 0
    if player.energy_limit - player.paid_consumption > 0:
        daily_energy_limit = player.energy_limit - player.paid_consumption

    groups = list(player.account.groups.all().values_list('name', flat=True))
    page = 'region/mining.html'
    if 'redesign' not in groups:
        page = 'region/redesign/mining.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': _('Добыча'),

        'player': player,
        'premium': premium,
        'auto_mining': auto_mining,

        'daily_limit': daily_limit,
        'daily_energy_limit': daily_energy_limit,
        'daily_procent': daily_procent,
        'daily_current_sum': daily_current_sum,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
