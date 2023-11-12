from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils import translation
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from factory.models.project import Project
from storage.models.storage import Storage
from factory.models.auto_produce import AutoProduce
from storage.models.good import Good
from storage.models.stock import Stock
from factory.models.blueprint import Blueprint
from factory.models.component import Component


@login_required(login_url='/')
@check_player
# Производство
def factory(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)
    storage_here = None

    premium = False

    if player.premium > timezone.now():
        premium = True

    fields_list = ['pk', 'region__id', 'region__region_name', 'region__on_map_id', 'cash', ]

    storages = Storage.actual.only(*fields_list).filter(owner=player)

    stocks = Stock.objects.filter(storage__in=storages)

    goods = Good.objects.all()

    total_stocks = {}
    good_names = {}
    good_by_type = {}

    first_storage = None

    for storage in storages:
        if not first_storage:
            first_storage = storage

        if player.region == storage.region:
            storage_here = storage

        total_stocks[storage.pk] = {}
        total_stocks[storage.pk]['Наличные'] = storage.cash
        good_names['Наличные'] = pgettext('goods', 'Наличные')

        for good in goods:
            good_names[good.pk] = good.name

            if good.type not in good_by_type.keys():
                good_by_type[good.type] = []

            good_by_type[good.type].append(good.pk)

            if stocks.filter(storage=storage, good=good).exists():
                total_stocks[storage.pk][good.pk] = stocks.get(storage=storage, good=good).stock

            else:
                total_stocks[storage.pk][good.pk] = 0


    # сколько игрок может производить на единичные затраты энергии
    consignment_dict = {}

    Standardization = apps.get_model('skill.Standardization')
    if Standardization.objects.filter(player=player, level__gt=0).exists():
        consignment_dict['materials'] = 1 + Standardization.objects.get(player=player).level

    MilitaryProduction = apps.get_model('skill.MilitaryProduction')
    if MilitaryProduction.objects.filter(player=player, level__gt=0).exists():
        consignment_dict['units'] = 1 + MilitaryProduction.objects.get(player=player).level

    # схемы производства
    schemas = {}

    blueprints = Blueprint.objects.all()
    components = Component.objects.all()

    for blueprint in blueprints:
        if not blueprint.good.pk in schemas:
            schemas[blueprint.good.pk] = {}

        schemas[blueprint.good.pk][blueprint.pk] = {}

        schemas[blueprint.good.pk][blueprint.pk]['energy'] = blueprint.energy_cost
        schemas[blueprint.good.pk][blueprint.pk]['Наличные'] = blueprint.cash_cost

        for component in components.filter(blueprint=blueprint):
            schemas[blueprint.good.pk][blueprint.pk][component.good.pk] = component.count

    # авто - производство
    auto_produce = None
    if AutoProduce.objects.filter(player=player).exists():
        auto_produce = AutoProduce.objects.get(player=player)

    # если есть производство на авто-показываем используемый склад
    if auto_produce:
        first_storage = auto_produce.storage
    # если мы в регионе со складом - показываем его
    # инчае - оставляем как есть
    elif storage_here:
        first_storage = storage_here


    groups = list(player.account.groups.all().values_list('name', flat=True))
    page = 'factory/factory.html'

    if 'redesign' not in groups:
        page = 'factory/redesign/factory.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('factory', 'Производство'),

        'player': player,
        'premium': premium,
        'auto': auto_produce,
        'first_storage': first_storage,

        'total_stocks': total_stocks,
        'good_by_type': good_by_type,
        'good_names': good_names,

        'schemas': schemas,

        'project_cl': Project,
        'storage_cl': Storage,
        'storages': storages,
        'consignment_dict': consignment_dict,
        'categories': ['materials', 'equipments', 'units'],
        'crude_list': ['valut', 'minerals', 'oils', 'materials', 'equipments'],
    })
    return response
