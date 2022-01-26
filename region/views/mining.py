from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player


# главная страница
@login_required(login_url='/')
@check_player
def mining(request):
    player = Player.objects.get(account=request.user)

    # 3500 - количество энергии, которую надо выфармить за день
    if player.paid_consumption >= 3500:
        daily_procent = 100
    else:
        daily_procent = player.energy_consumption / ((3500 - player.paid_consumption) / 100)

    if daily_procent > 100:
        daily_procent = 100

    # сумма, которую уже можно забрать
    daily_current_sum = int((14500 - player.paid_sum) / 100 * daily_procent)

    daily_energy_limit = 0
    if player.energy_limit - player.paid_consumption > 0:
        daily_energy_limit = player.energy_limit - player.paid_consumption

    # отправляем в форму
    response = render(request, 'region/mining.html', {
        'page_name': _('Добыча'),

        'player': player,

        'daily_energy_limit': daily_energy_limit,
        'daily_procent': daily_procent,
        'daily_current_sum': daily_current_sum,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
