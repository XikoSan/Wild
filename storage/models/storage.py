# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy, ugettext as _
from django.apps import apps
from player.actual_manager import ActualStorageManager
from player.player import Player
from region.models.region import Region
from django.utils.translation import pgettext


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
        'drilling': pgettext_lazy('goods', 'Буровые установки'),
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
        'mines': pgettext_lazy('goods', 'Мины'),

        'drone': pgettext_lazy('goods', 'БПЛА'),
    }

    sizes = {
        'large': ['coal', 'iron', 'bauxite', 'wti_oil', 'brent_oil', 'urals_oil' ],
        'medium': ['gas', 'diesel', 'plastic', 'steel', 'aluminium', 'medical', 'rifle' ],
        'small': ['tank', 'mines', 'antitank', 'jet', 'pzrk', 'ifv', 'drone', 'drilling'],
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

    # уровень прокачки. 1 - только пострен
    level = models.IntegerField(default=1, verbose_name=pgettext_lazy('storage', 'Уровень'))

    # наличные на складе
    cash = models.BigIntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Наличные'))

    # Большой типоразмер - максимум на складе
    large_cap = models.IntegerField(default=120000, verbose_name='Большой лимит') # 120 000 -> 600 000
    # Средний типоразмер - максимум на складе
    medium_cap = models.IntegerField(default=20000, verbose_name='Средний лимит') # 20 000 -> 100 000
    # Малый типоразмер - максимум на складе
    small_cap = models.IntegerField(default=2000, verbose_name='Малый лимит') # 2 000 -> 10 000

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    @staticmethod
    def get_good_text(good):
        good_text = None
        if good == 'cash':
            good_text = pgettext_lazy('goods', 'Наличные')

        else:
            for mode in Storage.types.keys():
                for unit in getattr(Storage, mode).keys():
                    if good == unit:
                        good_text = getattr(Storage, mode)[unit]
                        break

                if good_text:
                    break

        return good_text

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
        good_cl = apps.get_model('storage', 'Good')
        goods = good_cl.objects.filter(type=mode)
        stock_cl = apps.get_model('storage', 'Stock')
        data = {}

        stocks = stock_cl.objects.filter(storage=self, good__in=goods)

        for good in goods:
            if stocks.filter(good=good, stock__gt=0).exists():
                data[good.pk] = stocks.get(good=good, stock__gt=0).stock
            else:
                data[good.pk] = 0

        return data

    # получить информацию о количестве предметов
    def allStorageCount(self):
        good_cl = apps.get_model('storage', 'Good')
        goods = good_cl.objects.all()
        stock_cl = apps.get_model('storage', 'Stock')
        data = {}

        data['cash'] = getattr(self, 'cash')
        for mode in self.types.keys():
            # товары конкретной категории
            mode_goods = goods.filter(type=mode)

            stocks = stock_cl.objects.filter(storage=self, good__in=mode_goods)

            for good in mode_goods:
                if stocks.filter(good=good, stock__gt=0).exists():
                    data[good.pk] = stocks.get(good=good, stock__gt=0).stock
                else:
                    data[good.pk] = 0

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
                    return pgettext_lazy('goods', 'Передано отрицательное значение')
                    # return 'Нельзя списать со Склада отрицательное количество'
                if unit_cnt == 0:
                    continue
                if unit_cnt > getattr(self, unit):
                    return pgettext_lazy('goods', 'Недостаточно') + ' ' + str(getattr(self, mode).get(unit))
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
    def capacity_check(self, size, count, stocks):
        # передан ноль (ничего не передают)
        if count == 0:
            return True
        # передано отрицательное число
        if count < 0:
            return False
        # проверяем влезет ли всё - кроме денег
        if not size == 'cash':
            if count + stocks > getattr(self, size + '_cap'):
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
