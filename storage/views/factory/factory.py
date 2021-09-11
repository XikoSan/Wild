from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from storage.models.factory.project import Project
from storage.models.storage import Storage

@login_required(login_url='/')
@check_player
# Производство
def factory(request):
    # получаем персонажа
    player = Player.objects.get(account=request.user)

    fields_list = ['pk', 'region__region_name', 'cash', ]
    # собираем из Склада все поля ресурсов
    for category in Storage.types.keys():
        for good in getattr(Storage, category).keys():
            if good == 'station':
                continue
            fields_list.append(good)
            fields_list.append(good + '_cap')

    storages = Storage.actual.filter(owner=player).values(*fields_list)

    # отправляем в форму
    response = render(request, 'storage/factory/factory.html', {
        'page_name': _('Производство'),

        'player': player,
        'project_cl': Project,
        'storage_cl': Storage,
        'storages': storages,
        'categories': ['materials', 'units'],
        'crude_list': ['valut', 'minerals', 'oils', 'materials'],
    })
    return response
