# coding=utf-8
from django.db import models
from storage.models.storage import Storage
from player.logs.log import Log
from django.utils.translation import gettext_lazy
from storage.models.factory.project import Project


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
    coal = models.IntegerField(default=0, verbose_name=gettext_lazy('Уголь'))

    # Железо
    iron = models.IntegerField(default=0, verbose_name=gettext_lazy('iron'))

    # Бокситы
    bauxite = models.IntegerField(default=0, verbose_name=gettext_lazy('bauxite'))

    # ------vvvvvvv------Нефть на складе------vvvvvvv------
    # Нефть WTI
    wti_oil = models.IntegerField(default=0, verbose_name=gettext_lazy('wti_oil'))

    # Нефть Brent
    brent_oil = models.IntegerField(default=0, verbose_name=gettext_lazy('brent_oil'))

    # Нефть Urals
    urals_oil = models.IntegerField(default=0, verbose_name=gettext_lazy('urals_oil'))

    # ------vvvvvvv------Материалы на складе------vvvvvvv------
    # бензин
    gas = models.IntegerField(default=0, verbose_name=gettext_lazy('gas'))

    # бензин
    diesel = models.IntegerField(default=0, verbose_name=gettext_lazy('diesel'))

    steel = models.IntegerField(default=0, verbose_name=gettext_lazy('steel'))

    aluminium = models.IntegerField(default=0, verbose_name=gettext_lazy('alumunuim'))

    # ------vvvvvvv------Юниты на складе------vvvvvvv------
    # танки
    tank = models.IntegerField(default=0, verbose_name=gettext_lazy('tank'))

    # штурмовики
    jet = models.IntegerField(default=0, verbose_name=gettext_lazy('attack_air'))

    # орбитальные орудия
    station = models.IntegerField(default=0, verbose_name=gettext_lazy('orb_station'))

    # ПЗРК
    pzrk = models.IntegerField(default=0, verbose_name=gettext_lazy('mpads'))

    # AT-cannon
    antitank = models.IntegerField(default=0, verbose_name=gettext_lazy('antitank'))

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
