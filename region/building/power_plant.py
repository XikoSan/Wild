# coding=utf-8
from django.db import models
from django.utils import timezone
from player.views.get_subclasses import get_subclasses
from region.building.building import Building
from region.models.region import Region
from state.models.treasury import Treasury
from django.db.models import F
import datetime
from django.db import transaction
import time
# Электростанция - здание в регионе
class PowerPlant(Building):
    # сколько производит каждый уровень электростанции
    production = 10

    # сколько угля потребляет каждый уровень электры в час
    consumption = 20

    # # Включенный уровень здания
    # level_on = models.IntegerField(default=None, blank=True, null=True, verbose_name='Вкл. уровень здания')

    # # проверяем работоспособность электросети
    # @staticmethod
    # @transaction.atomic
    # def check_is_working(state):
    #     # получаем Казну госа
    #     treasury = Treasury.get_instance(state=state)
    #     # если электросеть работает и час еще не прошел - возвращаем ОК
    #     if treasury.power_on and (timezone.now() - treasury.power_actualize).total_seconds() < 3600:
    #         return True
    #
    #     # узнаем сколько раз по часу прошло
    #     counts = (timezone.now() - treasury.power_actualize).total_seconds() // 3600
    #
    #     if counts == 0:
    #         # если актуализировать не нужно, возвращаем текущее состояние
    #         return treasury.power_on
    #
    #     # остаток от деления понадобится чтобы указать время обновления
    #     modulo = (timezone.now() - treasury.power_actualize).total_seconds() % 3600
    #
    #     # узнаем, сколько потребляется электросетью угля
    #     cons = PowerPlant.get_coal_consumption(state=state)
    #
    #     # если угля достаточно
    #     if treasury.coal >= cons * counts:
    #         # списываем этот уголь, актуализируем казну
    #         treasury.coal -= cons * counts
    #         treasury.power_actualize = timezone.now()-datetime.timedelta(seconds=modulo)
    #         treasury.power_on = True
    #         treasury.save()
    #
    #         return True
    #
    #     # иначе - сеть не работает
    #     else:
    #         # списываем этот уголь, актуализируем казну
    #         treasury.power_actualize = timezone.now()-datetime.timedelta(seconds=modulo)
    #         treasury.power_on = False
    #         treasury.save()
    #
    #
    #         return False

    # получить строки с информацией об уровне и рейтинге здания
    @staticmethod
    def get_stat(region):

        if PowerPlant.objects.filter(region=region).exists():
            plant = PowerPlant.objects.get(region=region)

            level = plant.level

            # if plant.level_on:
            #     level_on = plant.level_on
            # else:
            #     level_on = None

        else:
            level = 0
            # level_on = None

        data = {
            'level': level,
            # 'level_on': level_on,
        }

        return data, 'region/redesign/buildings/power_plant.html'

    # # получить информацию о потреблении угля в госе
    # @staticmethod
    # def get_coal_consumption(state):
    #     # получаем электростанции всех регионов государства
    #     power_plants = PowerPlant.objects.filter(region__in=Region.objects.filter(state=state))
    #
    #     coal_consumption = 0
    #
    #     for plant in power_plants:
    #         if plant.level_on:
    #             coal_consumption += plant.level_on * PowerPlant.consumption
    #         else:
    #             coal_consumption += plant.level * PowerPlant.consumption
    #
    #     return coal_consumption

    # получить информацию о производстве элетричества в госе
    @staticmethod
    def get_power_production(state=None, region=None):

        if not state and not region:
            return 0

        if state:
            # получаем электростанции всех регионов государства
            power_plants = PowerPlant.objects.filter(region__in=Region.objects.filter(state=state))
        else:
            # получаем электростанции региона
            power_plants = PowerPlant.objects.filter(region=region)

        power_grid = 0

        for plant in power_plants:
            # if plant.level_on:
            #     power_grid += plant.level_on * PowerPlant.production
            # else:
            power_grid += plant.level * PowerPlant.production

        return power_grid

    # получить информацию о потреблении элетричества в госе
    @staticmethod
    def get_power_consumption(state=None, region=None):

        if not state and not region:
            return 0

        power_consumption = 0
        # получим классы всех строений
        building_classes = get_subclasses(Building)

        if state:
            # все реги государства
            regions = Region.objects.filter(state=state)
        else:
            regions = [region, ]

        # для каждого класса здания
        for building_cl in building_classes:
            # если такие здания есть в регах госа
            if building_cl.objects.filter(region__in=regions).exists():
                # считаем их потребление
                for building in building_cl.objects.filter(region__in=regions):
                    power_consumption += building.power_consumption * building.level

        return power_consumption

    # получить баланс электричества в государстве
    @staticmethod
    def get_power_balance(state=None, region=None):
        # узнаем производство
        power_production = PowerPlant.get_power_production(state, region)
        # узнаем потребление
        power_consumption = PowerPlant.get_power_consumption(state, region)
        # считаем разницу
        power_balance = power_production - power_consumption

        return power_balance

    # получить процент работающих зданий
    @staticmethod
    def get_power_efficiency(state=None, region=None):
        # узнаем производство
        power_production = PowerPlant.get_power_production(state, region)
        # узнаем потребление
        power_consumption = PowerPlant.get_power_consumption(state, region)

        # если потребителей нет, эффективность - 100%
        if power_consumption == 0:
            return 100
        # считаем процент
        else:
            efficiency = power_production * 100 / power_consumption

            if efficiency > 100:
                efficiency = 100

            return efficiency

    # Свойства класса
    class Meta:
        verbose_name = "ТЭЦ"
        verbose_name_plural = "Теплоэлектростанции"
