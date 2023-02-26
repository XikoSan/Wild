from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from factory.models.project import Project
from storage.models.storage import Storage


@login_required(login_url='/')
@check_player
# Производство
def factory(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    fields_list = ['pk', 'region__pk', 'region__region_name', 'cash', ]
    # собираем из Склада все поля ресурсов
    for category in Storage.types.keys():
        for good in getattr(Storage, category).keys():
            if good == 'station':
                continue
            fields_list.append(good)
            fields_list.append(good + '_cap')

    storages = Storage.actual.filter(owner=player).values(*fields_list)

    # сколько игрок может производить на единичные затраты энергии
    consignment_dict = {}

    Standardization = apps.get_model('skill.Standardization')
    if Standardization.objects.filter(player=player, level__gt=0).exists():
        consignment_dict['materials'] = 1 + Standardization.objects.get(player=player).level

    MilitaryProduction = apps.get_model('skill.MilitaryProduction')
    if MilitaryProduction.objects.filter(player=player, level__gt=0).exists():
        consignment_dict['units'] = 1 + MilitaryProduction.objects.get(player=player).level

    # отправляем в форму
    response = render(request, 'factory/factory.html', {
        'page_name': _('Производство'),

        'player': player,
        'project_cl': Project,
        'storage_cl': Storage,
        'storages': storages,
        'consignment_dict': consignment_dict,
        'categories': ['materials', 'equipments', 'units'],
        'crude_list': ['valut', 'minerals', 'oils', 'materials', 'equipments'],
    })
    return response
