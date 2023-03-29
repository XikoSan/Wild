# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy

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
        'wti_oil': 0.1,

        'brent_oil': 0.1,

        'urals_oil': 0.1,
    }
    # ------vvvvvvv------Материалы на складе------vvvvvvv------
    materials = {
        'gas': 0.1,

        'diesel': 0.1,

        'plastic': 0.2,

        # 'steel': 10,
        'steel': 1,

        'aluminium': 1,
        # 'aluminium': 10,
    }
    # ------vvvvvvv------Оборудование на складе------vvvvvvv------
    equipments = {
        # 'medical': 5,
        'medical': 0.5,
        'drilling': 2,
    }
    # ------vvvvvvv------Юниты на складе------vvvvvvv------
    units = {
        'rifle': 0.5,

        # 'tank': 105,
        'tank': 10.5,
        'antitank': 5,
        # 'antitank': 50,
        'mines': 4,
        # 'antitank': 50,

        # 'jet': 150,
        'jet': 15,
        # 'pzrk': 50,
        'pzrk': 5,

        'ifv': 4,
        # 'ifv': 40,

        'drone': 1,
        # 'ifv': 10,
    }

    # регион отправки
    storage_from = models.ForeignKey(Storage, default=None, null=True, on_delete=models.CASCADE,
                               verbose_name='Склад отправки', related_name='storage_from')

    # регион получения
    storage_to = models.ForeignKey(Storage, default=None, null=True, on_delete=models.CASCADE,
                               verbose_name='Склад получения', related_name='storage_to')


    # Количество занятых кубов всего
    total_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Всего кубов'))
    # стоимость доставки
    delivery_value = models.BigIntegerField(default=0, verbose_name='Стоимость доставки')
    # ------vvvvvvv------Минералы на складе------vvvvvvv------
    # Уголь
    coal = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Уголь'))
    # Уголь - количество занятых кубов
    coal_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Уголь - кубов'))

    # Железо
    iron = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Железо'))
    # Железо - кубов
    iron_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Железо - кубов'))

    # Бокситы
    bauxite = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Бокситы'))
    # Бокситы - кубов
    bauxite_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Бокситы - кубов'))

    # ------vvvvvvv------Нефть на складе------vvvvvvv------
    # Нефть WTI
    wti_oil = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Нефть WTI'))
    # Нефть WTI- кубов
    wti_oil_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'WTI - кубов'))

    # Нефть Brent
    brent_oil = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Нефть Brent'))
    # Нефть Brent- кубов
    brent_oil_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Brent - кубов'))

    # Нефть Urals
    urals_oil = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Нефть Urals'))
    # Нефть Urals- кубов
    urals_oil_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Urals - кубов'))

    # ------vvvvvvv------Материалы на складе------vvvvvvv------
    # бензин
    gas = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Бензин'))
    # бензин- кубов
    gas_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Бензин - кубов'))

    # бензин
    diesel = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Дизель'))
    # бензин- кубов
    diesel_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Дизель - кубов'))

    # пластик
    plastic = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Пластик'))
    # пластик- кубов
    plastic_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Пластик - кубов'))

    steel = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Сталь'))
    # сталь- максимум на складе
    steel_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Сталь - кубов'))

    aluminium = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Алюминий'))
    # сталь- максимум на складе
    aluminium_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Алюминий - кубов'))

    # ------vvvvvvv------Оборудование на складе------vvvvvvv------
    # Медикаменты
    medical = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Медикаменты'))
    # Автоматы- максимум на складе
    medical_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Медикаменты - кубов'))

    # ------vvvvvvv------Юниты на складе------vvvvvvv------
    # Автоматы
    rifle = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Автоматы'))
    # Автоматы- максимум на складе
    rifle_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Автоматы - кубов'))

    # танки
    tank = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Танки'))
    # танки- максимум на складе
    tank_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Танки - кубов'))

    # штурмовики
    jet = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Штурмовики'))
    # танки- максимум на складе
    jet_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Штурмовики - кубов'))

    # орбитальные орудия
    station = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Орбиталки'))
    # танки- максимум на складе
    station_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Орбиталки - кубов'))

    # ПЗРК
    pzrk = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'ПЗРК'))
    # танки- максимум на складе
    pzrk_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'ПЗРК - кубов'))

    # AT-cannon
    antitank = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'ПТ-пушка'))
    # танки- максимум на складе
    antitank_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'ПТ-пушка - кубов'))

    # Гаубица
    ifv = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'БМП'))
    # Гаубица - кубов
    ifv_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'БМП - кубов'))

    # Дроны
    drone = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Дроны'))
    # Дроны - кубов
    drone_vol = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Дроны - кубов'))

    def __str__(self):
        return self.storage_from.owner.nickname + " (" + self.storage_from.region.region_name + ") " + '-> ' + self.storage_to.owner.nickname + " (" + self.storage_to.region.region_name + ")"

    # Свойства класса
    class Meta:
        verbose_name = "Транспорт"
        verbose_name_plural = "Транспорты"
