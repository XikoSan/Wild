import math
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from region.views.distance_counting import distance_counting
from storage.models.storage import Storage
from storage.models.transport import Transport


# главная страница
@login_required(login_url='/')
@check_player
def assets(request):
    player = Player.objects.get(account=request.user)
    # словарь склад - словарь стоимости до других регионов со складами:
    # москва:
    # - архангельск = 15
    # - питер       = 8
    # - моск. обл.  = 1
    trans_mul = {}

    # получаем все склады
    storages = Storage.actual.filter(owner=player)

    for storage in storages:
        trans_mul[storage.pk] = {}
        for dest in storages:
            if not dest == storage:
                trans_mul[storage.pk][dest.pk] = math.ceil(distance_counting(storage.region, dest.region) / 100)

    # отправляем в форму
    response = render(request, 'storage/assets.html', {
        'page_name': _('Активы'),

        'player': player,
        'storages': storages,

        'transport': Transport,
        'storage_cl': Storage,
        'trans_mul': trans_mul,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
