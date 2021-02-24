# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy

from player.logs.log import Log
from player.player import Player
from storage.models.storage import Storage


class Transport(Log):
    # концепция:
    # игрок платит за неполный "куб" пространства, занятого при транспортировке
    # таким образом, он может перевезти 333 бокситов в одном кубе
    # при попытке перевезти 334 единицы руды он будет платить за два "куба" емкости

    # ------vvvvvvv------Минералы на складе------vvvvvvv------
    minerals = {
        # Уголь
        'coal': 0.007,
        # Железо
        'iron': 0.005,
        # Бокситы
        'bauxite': 0.003,
    }
    # ------vvvvvvv------Нефть на складе------vvvvvvv------
    oils = {
        'wti_oil': 1,

        'brent_oil': 1,

        'urals_oil': 1,
    }
    # ------vvvvvvv------Материалы на складе------vvvvvvv------
    materials = {
        'gas': 1,

        'diesel': 1,

        'steel': 10,

        'aluminium': 10,
    }
    # ------vvvvvvv------Юниты на складе------vvvvvvv------
    units = {
        'tank': 105,
        'antitank': 50,

        'jet': 150,
        'pzrk': 50,
    }

    # регион отправки
    storage_from = models.ForeignKey(Storage, default=None, null=True, on_delete=models.CASCADE,
                               verbose_name='Склад отправки', related_name='storage_from')

    # регион получения
    storage_to = models.ForeignKey(Storage, default=None, null=True, on_delete=models.CASCADE,
                               verbose_name='Склад получения', related_name='storage_to')


    # Количество занятых кубов всего
    total_vol = models.IntegerField(default=0, verbose_name=gettext_lazy('Всего кубов'))
    # ------vvvvvvv------Минералы на складе------vvvvvvv------
    # Уголь
    coal = models.IntegerField(default=0, verbose_name=gettext_lazy('Уголь'))
    # Уголь - количество занятых кубов
    coal_vol = models.IntegerField(default=0, verbose_name=gettext_lazy('Уголь - кубов'))

    # Железо
    iron = models.IntegerField(default=0, verbose_name=gettext_lazy('iron'))
    # Железо - кубов
    iron_vol = models.IntegerField(default=0, verbose_name=gettext_lazy('Железо - кубов'))

    # Бокситы
    bauxite = models.IntegerField(default=0, verbose_name=gettext_lazy('bauxite'))
    # Бокситы - кубов
    bauxite_vol = models.IntegerField(default=0, verbose_name=gettext_lazy('Бокситы - кубов'))

    # ------vvvvvvv------Нефть на складе------vvvvvvv------
    # Нефть WTI
    wti_oil = models.IntegerField(default=0, verbose_name=gettext_lazy('wti_oil'))
    # Нефть WTI- кубов
    wti_oil_vol = models.IntegerField(default=0, verbose_name=gettext_lazy('wti_oil_cap'))

    # Нефть Brent
    brent_oil = models.IntegerField(default=0, verbose_name=gettext_lazy('brent_oil'))
    # Нефть Brent- кубов
    brent_oil_vol = models.IntegerField(default=0, verbose_name=gettext_lazy('brent_oil_cap'))

    # Нефть Urals
    urals_oil = models.IntegerField(default=0, verbose_name=gettext_lazy('urals_oil'))
    # Нефть Urals- кубов
    urals_oil_vol = models.IntegerField(default=0, verbose_name=gettext_lazy('urals_oil_cap'))

    # ------vvvvvvv------Материалы на складе------vvvvvvv------
    # бензин
    gas = models.IntegerField(default=0, verbose_name=gettext_lazy('gas'))
    # бензин- кубов
    gas_vol = models.IntegerField(default=0, verbose_name=gettext_lazy('gas_cap'))

    # бензин
    diesel = models.IntegerField(default=0, verbose_name=gettext_lazy('diesel'))
    # бензин- кубов
    diesel_vol = models.IntegerField(default=0, verbose_name=gettext_lazy('diesel_cap'))

    steel = models.IntegerField(default=0, verbose_name=gettext_lazy('steel'))
    # сталь- максимум на складе
    steel_vol = models.IntegerField(default=0, verbose_name=gettext_lazy('steel_cap'))

    aluminium = models.IntegerField(default=0, verbose_name=gettext_lazy('alumunuim'))
    # сталь- максимум на складе
    aluminium_vol = models.IntegerField(default=0, verbose_name=gettext_lazy('alumunuim_cap'))

    # ------vvvvvvv------Юниты на складе------vvvvvvv------
    # танки
    tank = models.IntegerField(default=0, verbose_name=gettext_lazy('tank'))
    # танки- максимум на складе
    tank_vol = models.IntegerField(default=0, verbose_name='Танки- максимум на складе')

    # штурмовики
    jet = models.IntegerField(default=0, verbose_name=gettext_lazy('attack_air'))
    # танки- максимум на складе
    jet_vol = models.IntegerField(default=0, verbose_name='Штурмовики- максимум на складе')

    # орбитальные орудия
    station = models.IntegerField(default=0, verbose_name=gettext_lazy('orb_station'))
    # танки- максимум на складе
    station_vol = models.IntegerField(default=0, verbose_name='Орбитальные орудия- максимум на складе')

    # ПЗРК
    pzrk = models.IntegerField(default=0, verbose_name=gettext_lazy('mpads'))
    # танки- максимум на складе
    pzrk_vol = models.IntegerField(default=0, verbose_name='ПЗРК- максимум на складе')

    # AT-cannon
    antitank = models.IntegerField(default=0, verbose_name=gettext_lazy('antitank'))
    # танки- максимум на складе
    antitank_vol = models.IntegerField(default=0, verbose_name='ПТ-пушка- максимум на складе')

    def __str__(self):
        return self.storage_from.owner.nickname + " (" + self.storage_from.region.region_name + ") " + '-> ' + self.storage_to.owner.nickname + " (" + self.storage_to.region.region_name + ")"

    # Свойства класса
    class Meta:
        verbose_name = "Транспорт"
        verbose_name_plural = "Транспорты"
