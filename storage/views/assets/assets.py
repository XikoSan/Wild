import math
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from region.views.distance_counting import distance_counting
from storage.models.storage import Storage
from storage.models.transport import Transport
from datetime import datetime


# главная страница
@login_required(login_url='/')
@check_player
def assets(request):
    player = Player.get_instance(account=request.user)
    # словарь склад - словарь стоимости до других регионов со складами:
    # москва:
    # - архангельск = 15
    # - питер       = 8
    # - моск. обл.  = 1
    trans_mul = {}

    # получаем все склады
    storages = Storage.objects.filter(owner=player)

    storage_alone = False
    if storages.count() == 1:
        storage_alone = True

    for storage in storages:
        trans_mul[storage.pk] = {}
        for dest in storages:
            if not dest == storage:
                trans_mul[storage.pk][dest.pk] = math.ceil(distance_counting(storage.region, dest.region) / 100)

    groups = list(player.account.groups.all().values_list('name', flat=True))
    page = 'storage/assets.html'
    if 'redesign' not in groups:
        page = 'storage/redesign/assets.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': _('Активы'),

        'player': player,
        'storages': storages,

        'storage_alone': storage_alone,

        'transport': Transport,
        'storage_cl': Storage,
        'trans_mul': trans_mul,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
