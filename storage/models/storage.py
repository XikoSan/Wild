# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy, ugettext as _

from player.actual_manager import ActualStorageManager
from player.player import Player
from region.region import Region


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
    actual = ActualStorageManager()  # Менеджер активных записей

    # ------vvvvvvv------Все типы товаров------vvvvvvv------
    types = {
        'minerals': pgettext_lazy('goods', 'Минералы'),
        'oils': pgettext_lazy('goods', 'Нефть'),
        'materials': pgettext_lazy('goods', 'Материалы'),
        'equipments': pgettext_lazy('goods', 'Оборудование'),
        'units': pgettext_lazy('goods', 'Оружие'),
    }
    # ------vvvvvvv------Деньги на складе------vvvvvvv------
    valut = {
        'cash': pgettext_lazy('goods', 'Наличные'),
    }
    # ------vvvvvvv------Минералы на складе------vvvvvvv------
    minerals = {
        # Уголь
        'coal': pgettext_lazy('goods', 'Уголь'),
        # Железо
        'iron': pgettext_lazy('goods', 'Железо'),
        # Бокситы
        'bauxite': pgettext_lazy('goods', 'Бокситы'),
    }
    # ------vvvvvvv------Нефть на складе------vvvvvvv------
    oils = {
        'wti_oil': pgettext_lazy('goods', 'Нефть WTI'),

        'brent_oil': pgettext_lazy('goods', 'Нефть Brent'),

        'urals_oil': pgettext_lazy('goods', 'Нефть Urals'),
    }
    # ------vvvvvvv------Материалы на складе------vvvvvvv------
    materials = {
        'gas': pgettext_lazy('goods', 'Бензин'),

        'diesel': pgettext_lazy('goods', 'Дизельное топливо'),

        'plastic': pgettext_lazy('goods', 'Пластик'),

        'steel': pgettext_lazy('goods', 'Сталь'),

        'aluminium': pgettext_lazy('goods', 'Алюминий'),
    }
    # ------vvvvvvv------Оборудование на складе------vvvvvvv------
    equipments = {
        'medical': pgettext_lazy('goods', 'Медикаменты'),
    }
    # ------vvvvvvv------Юниты на складе------vvvvvvv------
    units = {
        'rifle': pgettext_lazy('goods', 'Автоматы'),

        'tank': pgettext_lazy('goods', 'Танки'),
        'antitank': pgettext_lazy('goods', 'ПТ-орудия'),
        'station': pgettext_lazy('goods', 'Орбитальные орудия'),

        'jet': pgettext_lazy('goods', 'Штурмовики'),
        'pzrk': pgettext_lazy('goods', 'ПЗРК'),

        'ifv': pgettext_lazy('goods', 'БМП'),

        'drone': pgettext_lazy('goods', 'БПЛА'),
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
    cash = models.BigIntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Наличные'))

    # ------vvvvvvv------Минералы на складе------vvvvvvv------
    # Уголь
    coal = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Уголь'))
    # Уголь- максимум на складе
    coal_cap = models.IntegerField(default=100000, verbose_name=pgettext_lazy('goods', 'Уголь - лимит'))

    # Железо
    iron = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Железо'))
    # Железо- максимум на складе
    iron_cap = models.IntegerField(default=100000, verbose_name=pgettext_lazy('goods', 'Железо - лимит'))

    # Бокситы
    bauxite = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Бокситы'))
    # Бокситы- максимум на складе
    bauxite_cap = models.IntegerField(default=100000, verbose_name=pgettext_lazy('goods', 'Бокситы - лимит'))

    # ------vvvvvvv------Нефть на складе------vvvvvvv------
    # Нефть WTI
    wti_oil = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Нефть WTI'))
    # Нефть WTI- максимум на складе
    wti_oil_cap = models.IntegerField(default=100000, verbose_name=pgettext_lazy('goods', 'Нефть WTI - лимит'))

    # Нефть Brent
    brent_oil = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Нефть Brent'))
    # Нефть Brent- максимум на складе
    brent_oil_cap = models.IntegerField(default=100000, verbose_name=pgettext_lazy('goods', 'Нефть Brent - лимит'))

    # Нефть Urals
    urals_oil = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Нефть Urals'))
    # Нефть Urals- максимум на складе
    urals_oil_cap = models.IntegerField(default=100000, verbose_name=pgettext_lazy('goods', 'Нефть Urals - лимит'))

    # ------vvvvvvv------Материалы на складе------vvvvvvv------
    # бензин
    gas = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Бензин'))
    # бензин- максимум на складе
    gas_cap = models.IntegerField(default=10000, verbose_name=pgettext_lazy('goods', 'Бензин - лимит'))

    # бензин
    diesel = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Дизельное топливо'))
    # бензин- максимум на складе
    diesel_cap = models.IntegerField(default=10000, verbose_name=pgettext_lazy('goods', 'Дизельное топливо - лимит'))

    # пластик
    plastic = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Пластик'))
    # пластик- максимум на складе
    plastic_cap = models.IntegerField(default=10000, verbose_name=pgettext_lazy('goods', 'Пластик - лимит'))

    steel = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Сталь'))
    # сталь- максимум на складе
    steel_cap = models.IntegerField(default=10000, verbose_name=pgettext_lazy('goods', 'Сталь - лимит'))

    aluminium = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Алюминий'))
    # сталь- максимум на складе
    aluminium_cap = models.IntegerField(default=10000, verbose_name=pgettext_lazy('goods', 'Алюминий - лимит'))

    # ------vvvvvvv------Оборудование на складе------vvvvvvv------
    # Медикаменты
    medical = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Медикаменты'))
    # Медикаменты- максимум на складе
    medical_cap = models.IntegerField(default=10000, verbose_name=pgettext_lazy('goods', 'Медикаменты - лимит'))

    # ------vvvvvvv------Юниты на складе------vvvvvvv------
    # Автоматы
    rifle = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Автоматы'))
    # Автоматы- максимум на складе
    rifle_cap = models.IntegerField(default=10000, verbose_name=pgettext_lazy('goods', 'Автоматы - лимит'))

    # ПТ-пушка
    antitank = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'ПТ-орудия'))
    # танки- максимум на складе
    antitank_cap = models.IntegerField(default=1000, verbose_name=pgettext_lazy('goods', 'ПТ-орудия - лимит'))

    # танки
    tank = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Танки'))
    # танки- максимум на складе
    tank_cap = models.IntegerField(default=1000, verbose_name=pgettext_lazy('goods', 'Танки - лимит'))

    # штурмовики
    jet = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Штурмовики'))
    # штурмовики- максимум на складе
    jet_cap = models.IntegerField(default=1000, verbose_name=pgettext_lazy('goods', 'Штурмовики - лимит'))

    # орбитальные орудия
    station = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Орбитальные орудия'))
    # орудия- максимум на складе
    station_cap = models.IntegerField(default=10, verbose_name=pgettext_lazy('goods', 'Орбитальные орудия - лимит'))

    # ПЗРК
    pzrk = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'ПЗРК'))
    # ПЗРК- максимум на складе
    pzrk_cap = models.IntegerField(default=1000, verbose_name=pgettext_lazy('goods', 'ПЗРК - лимит'))

    # БМП
    ifv = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'БМП'))
    # БМП- максимум на складе
    ifv_cap = models.IntegerField(default=1000, verbose_name=pgettext_lazy('goods', 'БМП - лимит'))

    # дроны
    drone = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'БПЛА'))
    # дроны- максимум на складе
    drone_cap = models.IntegerField(default=1000, verbose_name=pgettext_lazy('goods', 'БПЛА - лимит'))

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    @staticmethod
    def get_choises(mode=None):
        choises = []

        for type in Storage.types.keys():
            if mode and mode != type:
                continue
            for good in getattr(Storage, type).keys():
                choises.append((good, getattr(Storage, type)[good]))

        return choises

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
        for mode in self.types.keys():
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
        Storage.actual.filter(pk=self.pk).update(**data_dict)

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
        Storage.actual.filter(pk=self.pk).update(**data_dict)

    def __str__(self):
        return self.owner.nickname + " в " + self.region.region_name

    # Свойства класса
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['owner', 'region'], name='one_in_region')
        ]
        verbose_name = "Склад"
        verbose_name_plural = "Склады"

    # =================================Запасы оружия во всех регионах игры
    # select
    # reg.region_name as "регион",
    # SUM(rifle) as "автоматы",
    # SUM(tank) as "танки",
    # SUM(antitank) as "ПТ",
    # SUM(station) as "орбиталки",
    # SUM(jet) as "штурмы",
    # SUM(pzrk) as "ПЗРК",
    # SUM(ifv) as "БМП",
    # SUM(drone) as "БПЛА"
    #
    # from storage_storage as st
    #
    # join
    # region_region as reg
    # on
    # reg.id = st.region_id
    # where
    # region_id in (
    #     select id from region_region
    # )
    # and deleted = false
    # group
    # by
    # reg.region_name
