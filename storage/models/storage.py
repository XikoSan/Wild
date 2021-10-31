# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy

from player.player import Player
from region.region import Region
from player.actual_manager import ActualManager
from django.utils.translation import ugettext as _


# Важная информация!
# При добавлении / изменении полей:

# - Если это товар:
# - - Добавить в списки по типам товаров
# - - Добавить в transport.py
# - - Добавить в destroy.py
# - - Добавить в treasury.py
# - - Добавить в trade_offer.py
# - - Добавить в good_lock.py

# - Если его можно производить:
# - - Добавить в project.py (саму схему и список схем внизу)
# - - Добавить в production_log.py
class Storage(models.Model):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей

    # ------vvvvvvv------Все типы товаров------vvvvvvv------
    types = {
        'minerals': gettext_lazy('Минералы'),
        'oils': gettext_lazy('Нефть'),
        'materials': gettext_lazy('Материалы'),
        'units': gettext_lazy('Оружие'),
    }
    # ------vvvvvvv------Деньги на складе------vvvvvvv------
    valut = {
        'cash': gettext_lazy('Наличные'),
    }
    # ------vvvvvvv------Минералы на складе------vvvvvvv------
    minerals = {
        # Уголь
        'coal': gettext_lazy('Уголь'),
        # Железо
        'iron': gettext_lazy('Железо'),
        # Бокситы
        'bauxite': gettext_lazy('Бокситы'),
    }
    # ------vvvvvvv------Нефть на складе------vvvvvvv------
    oils = {
        'wti_oil': gettext_lazy('Нефть WTI'),

        'brent_oil': gettext_lazy('Нефть Brent'),

        'urals_oil': gettext_lazy('Нефть Urals'),
    }
    # ------vvvvvvv------Материалы на складе------vvvvvvv------
    materials = {
        'gas': gettext_lazy('Бензин'),

        'diesel': gettext_lazy('Дизельное топливо'),

        'steel': gettext_lazy('Сталь'),

        'aluminium': gettext_lazy('Алюминий'),
    }
    # ------vvvvvvv------Юниты на складе------vvvvvvv------
    units = {
        'rifle': gettext_lazy('Автоматы'),

        'tank': gettext_lazy('Танки'),
        'antitank': gettext_lazy('ПТ-орудия'),
        'station': gettext_lazy('Орбитальные орудия'),

        'jet': gettext_lazy('Штурмовики'),
        'pzrk': gettext_lazy('ПЗРК'),

        'ifv': gettext_lazy('БМП'),
    }

    # владелец склада
    owner = models.ForeignKey(Player, default=None, null=True, on_delete=models.CASCADE, verbose_name='Владелец',
                              related_name="owner")
    # регион размещения
    region = models.ForeignKey(Region, default=None, null=True, on_delete=models.SET_NULL,
                               verbose_name='Регион размещения',
                               related_name="placement")

    # Показатель того, что склад уже переносился хоть раз
    was_moved = models.BooleanField(default=False, null=False, verbose_name='Переносился')

    # наличные на складе
    cash = models.BigIntegerField(default=0, verbose_name=gettext_lazy('storage_cash'))

    # ------vvvvvvv------Минералы на складе------vvvvvvv------
    # Уголь
    coal = models.IntegerField(default=0, verbose_name=gettext_lazy('Уголь'))
    # Уголь- максимум на складе
    coal_cap = models.IntegerField(default=100000, verbose_name=gettext_lazy('coal_cap'))

    # Железо
    iron = models.IntegerField(default=0, verbose_name=gettext_lazy('iron'))
    # Железо- максимум на складе
    iron_cap = models.IntegerField(default=100000, verbose_name=gettext_lazy('iron_cap'))

    # Бокситы
    bauxite = models.IntegerField(default=0, verbose_name=gettext_lazy('bauxite'))
    # Бокситы- максимум на складе
    bauxite_cap = models.IntegerField(default=100000, verbose_name=gettext_lazy('bauxite_cap'))

    # ------vvvvvvv------Нефть на складе------vvvvvvv------
    # Нефть WTI
    wti_oil = models.IntegerField(default=0, verbose_name=gettext_lazy('wti_oil'))
    # Нефть WTI- максимум на складе
    wti_oil_cap = models.IntegerField(default=100000, verbose_name=gettext_lazy('wti_oil_cap'))

    # Нефть Brent
    brent_oil = models.IntegerField(default=0, verbose_name=gettext_lazy('brent_oil'))
    # Нефть Brent- максимум на складе
    brent_oil_cap = models.IntegerField(default=100000, verbose_name=gettext_lazy('brent_oil_cap'))

    # Нефть Urals
    urals_oil = models.IntegerField(default=0, verbose_name=gettext_lazy('urals_oil'))
    # Нефть Urals- максимум на складе
    urals_oil_cap = models.IntegerField(default=100000, verbose_name=gettext_lazy('urals_oil_cap'))

    # ------vvvvvvv------Материалы на складе------vvvvvvv------
    # бензин
    gas = models.IntegerField(default=0, verbose_name=gettext_lazy('gas'))
    # бензин- максимум на складе
    gas_cap = models.IntegerField(default=10000, verbose_name=gettext_lazy('gas_cap'))

    # бензин
    diesel = models.IntegerField(default=0, verbose_name=gettext_lazy('diesel'))
    # бензин- максимум на складе
    diesel_cap = models.IntegerField(default=10000, verbose_name=gettext_lazy('diesel_cap'))

    steel = models.IntegerField(default=0, verbose_name=gettext_lazy('steel'))
    # сталь- максимум на складе
    steel_cap = models.IntegerField(default=10000, verbose_name=gettext_lazy('steel_cap'))

    aluminium = models.IntegerField(default=0, verbose_name=gettext_lazy('alumunuim'))
    # сталь- максимум на складе
    aluminium_cap = models.IntegerField(default=10000, verbose_name=gettext_lazy('alumunuim_cap'))

    # ------vvvvvvv------Юниты на складе------vvvvvvv------
    # Автоматы
    rifle = models.IntegerField(default=0, verbose_name=gettext_lazy('Автоматы'))
    # Автоматы- максимум на складе
    rifle_cap = models.IntegerField(default=10000, verbose_name='Автоматы- максимум на складе')

    # ПТ-пушка
    antitank = models.IntegerField(default=0, verbose_name=gettext_lazy('antitank'))
    # танки- максимум на складе
    antitank_cap = models.IntegerField(default=1000, verbose_name='ПТ-пушка- максимум на складе')

    # танки
    tank = models.IntegerField(default=0, verbose_name=gettext_lazy('tank'))
    # танки- максимум на складе
    tank_cap = models.IntegerField(default=1000, verbose_name='Танки- максимум на складе')

    # штурмовики
    jet = models.IntegerField(default=0, verbose_name=gettext_lazy('attack_air'))
    # танки- максимум на складе
    jet_cap = models.IntegerField(default=1000, verbose_name='Штурмовики- максимум на складе')

    # орбитальные орудия
    station = models.IntegerField(default=0, verbose_name=gettext_lazy('orb_station'))
    # танки- максимум на складе
    station_cap = models.IntegerField(default=10, verbose_name='Орбитальные орудия- максимум на складе')

    # ПЗРК
    pzrk = models.IntegerField(default=0, verbose_name=gettext_lazy('mpads'))
    # танки- максимум на складе
    pzrk_cap = models.IntegerField(default=1000, verbose_name='ПЗРК- максимум на складе')

    # Гаубицы
    ifv = models.IntegerField(default=0, verbose_name=gettext_lazy('БМП'))
    # танки- максимум на складе
    ifv_cap = models.IntegerField(default=1000, verbose_name='БМП- максимум на складе')

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    # получить информацию о количестве предметов
    def unitsOnStorageCount(self, mode):
        data = {}

        for unit in getattr(self, mode).keys():
            data[unit] = getattr(self, unit)

        return data

    # получить информацию о количестве предметов
    def allStorageCount(self):
        data = {}
        data['cash'] = getattr(self, 'cash')
        for mode in {'minerals', 'oils', 'materials', 'units'}:
            for unit in getattr(self, mode).keys():
                data[unit] = getattr(self, unit)

        return data

    # проверить наличие предметов на Складе
    def unitsOnStorageExist(self, request, mode):
        unit_cnt = 0
        retcode = False
        for unit in getattr(self, mode).keys():
            # проверяем что передано целое положительное число
            try:
                unit_cnt = int(request.POST.get(unit, ''))
                # передано отрицательное число
                if unit_cnt < 0:
                    return _('positive_spend_stock_req')
                    # return 'Нельзя списать со Склада отрицательное количество'
                if unit_cnt == 0:
                    continue
                if unit_cnt > getattr(self, unit):
                    return _('not_enough') + ' ' + str(getattr(self, mode).get(unit))
                    # return 'Не хватает на складе: ' + str(getattr(self, mode).get(unit))
                else:
                    retcode = True
            # нет юнита в запросе, ищем дальше
            except ValueError:
                continue
        # Если цикл прошел, а так ничего не нашлось
        if not retcode:
            return 0

    # проверить наличие места для предметов на Складе
    def capacity_check(self, field, count):
        # передан ноль (ничего не передают)
        if count == 0:
            return True
        # передано отрицательное число
        if count < 0:
            return False
        # проверяем влезет ли всё - кроме денег
        if not field == 'cash':
            if count + getattr(self, field) > getattr(self, field + '_cap'):
                return False
            else:
                return True
        else:
            # Для денег место есть всегда
            return True

    # списать предметы со Склада
    def unitsOnStorageUsing(self, request, mode):
        data_dict = {}
        for unit in getattr(self, mode).keys():
            # проверяем что передано целое положительное число
            try:
                unit_cnt = int(request.POST.get(unit, ''))
                # передано отрицательное число
                if unit_cnt < 0:
                    return
                # предметов нужно больше чем есть на складе
                if unit_cnt > getattr(self, unit):
                    return
                # записываем новое число предметов на складе
                data_dict[unit] = getattr(self, unit) - unit_cnt
            # нет юнита в запросе, ищем дальше
            except ValueError:
                continue
        # списываем предметы
        Storage.objects.filter(pk=self.pk).update(**data_dict)

    # начислить предметы на Склад
    def unitsToStorageAdd(self, request, mode):
        data_dict = {}
        for unit in getattr(self, mode).keys():
            # проверяем что передано целое положительное число
            try:
                unit_cnt = int(request.POST.get(unit, ''))
                # передано отрицательное число
                if unit_cnt < 0:
                    return
                # предметов добавляется больше чем может вместить Склад
                if not unit == 'cash':
                    if unit_cnt + getattr(self, unit) > getattr(self, unit + '_cap'):
                        return
                # записываем новое число предметов на складе
                data_dict[unit] = getattr(self, unit) + unit_cnt
            # нет юнита в запросе, ищем дальше
            except ValueError:
                continue
        # начисляем предметы
        Storage.objects.filter(pk=self.pk).update(**data_dict)

    def __str__(self):
        return self.owner.nickname + " в " + self.region.region_name

    # Свойства класса
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['owner', 'region'], name='one_in_region')
        ]
        verbose_name = "Склад"
        verbose_name_plural = "Склады"
