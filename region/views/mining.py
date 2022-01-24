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

    # сумма минимальной выплаты, зависящая от уровня медки
    energy_increase = 0

    if player.region.med_top == 5:
        energy_increase += 16
    elif player.region.med_top == 4:
        energy_increase += 13
    elif player.region.med_top == 3:
        energy_increase += 12
    elif player.region.med_top == 2:
        energy_increase += 11
    else:
        energy_increase += 9
    # количество интервалов по 10 минут в сутках * прирост = сумма прироста энергии за день
    dole = 144 * energy_increase

    # если есть запись о том, что человек сегодня собирал деньги - значит, забирал и мин. выплату
    cash_log_cl = apps.get_model('player.CashLog')
    if cash_log_cl.objects.filter(player=player, dtime__gt=timezone.now().date(), activity_txt='daily').exists()\
            and player.paid_sum == 0:
        player.paid_sum += cash_log_cl.objects.filter(dtime__gt=timezone.now().date(), activity_txt='daily').order_by(
            'dtime').first().cash
        player.save()
        dole = 0
    # если игрок уже сегодня забирал деньги, значит, забирал и минимальную выплату
    if player.paid_sum > 0:
        dole = 0

    # сумма, которую уже можно забрать
    daily_current_sum = int((14500 - player.paid_sum - dole) / 100 * daily_procent)

    daily_current_sum += dole

    daily_energy_limit = 0
    if 3500 - player.paid_consumption > 0:
        daily_energy_limit = 3500 - player.paid_consumption

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
