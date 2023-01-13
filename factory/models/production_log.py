# coding=utf-8
from django.db import models
from storage.models.storage import Storage
from player.logs.log import Log
from django.utils.translation import gettext_lazy, pgettext_lazy
from factory.models.project import Project


# Лог торговли
class ProductionLog(Log):
    # склад производства
    prod_storage = models.ForeignKey(Storage, default=None, null=True, on_delete=models.CASCADE,
                                     verbose_name='Склад производства', related_name="production_storage")

    prod_result = models.CharField(max_length=50, verbose_name='Продукция')

    # наличные на складе
    cash = models.BigIntegerField(default=0, verbose_name=gettext_lazy('storage_cash'))

    # ------vvvvvvv------Минералы на складе------vvvvvvv------
    # Уголь
    coal = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Наличные'))

    # Железо
    iron = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Железо'))

    # Бокситы
    bauxite = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Бокситы'))

    # ------vvvvvvv------Нефть на складе------vvvvvvv------
    # Нефть WTI
    wti_oil = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Нефть WTI'))

    # Нефть Brent
    brent_oil = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Нефть Brent'))

    # Нефть Urals
    urals_oil = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Нефть Urals'))

    # ------vvvvvvv------Материалы на складе------vvvvvvv------
    # бензин
    gas = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Бензин'))

    # бензин
    diesel = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Дизельное топливо'))

    # пластик
    plastic = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Пластик'))

    steel = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Сталь'))

    aluminium = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Алюминий'))

    # ------vvvvvvv------Оборудование на складе------vvvvvvv------
    # Медикаменты
    medical = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Медикаменты'))

    # ------vvvvvvv------Юниты на складе------vvvvvvv------
    # Автоматы
    rifle = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Автоматы'))

    # танки
    tank = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Танки'))

    # штурмовики
    jet = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Штурмовики'))

    # орбитальные орудия
    station = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Орбитальные орудия'))

    # ПЗРК
    pzrk = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'ПЗРК'))

    # AT-cannon
    antitank = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'ПТ-орудия'))

    # Гаубицы
    ifv = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'БМП'))

    def __str__(self):
        good_name = self.prod_result
        for schema in Project.schemas:
            if schema[0] == good_name:
                good_name = schema[1]
                break

        return str(self.dtime.strftime('%Y-%m-%d %H:%M')) + ", " + self.player.nickname + ": " + \
               str(good_name) + " в " + str(self.prod_storage.region.region_name)

    # Свойства класса
    class Meta:
        verbose_name = "Лог производства"
        verbose_name_plural = "Логи производства"
