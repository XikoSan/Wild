# coding=utf-8
from django.db import models
from storage.models.storage import Storage
from player.logs.log import Log
from django.utils.translation import gettext_lazy, pgettext_lazy
from factory.models.project import Project
from storage.models.good import Good


# Лог торговли
class ProductionLog(Log):
    # склад производства
    prod_storage = models.ForeignKey(Storage, default=None, null=True, on_delete=models.CASCADE,
                                     verbose_name='Склад производства', related_name="production_storage")

    # вид движения
    good_move_choices = (
        ('incom', 'Приход'),
        ('outcm', 'Расход'),
    )

    good_move = models.CharField(
        max_length=5,
        choices=good_move_choices,
        default='incom',
        verbose_name='Тип движения',
    )

    # производимый товар
    good_choices = (('cash', pgettext_lazy('goods', 'Наличные')), )
    for mode in Storage.types.keys():
        for unit in getattr(Storage, mode).keys():
            good_choices = good_choices + ((unit, getattr(Storage, mode)[unit]),)

    old_good = models.CharField(
        max_length=20,
        choices=good_choices,
        default=None, blank=True, null=True,
        verbose_name='устарело',
    )

    # признак блокированных денег вместо товара
    cash = models.BooleanField(default=False, verbose_name='Наличные')

    # товар для производства
    good = models.ForeignKey(Good, default=None, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Товар')

    # объем производства
    prod_value = models.IntegerField(default=1, verbose_name='Объем производства')

    def __str__(self):

        good_text = None
        if self.good == 'cash':
            good_text = pgettext_lazy('goods', 'Наличные')

        else:
            for mode in Storage.types.keys():
                for unit in getattr(Storage, mode).keys():
                    if self.good == unit:
                        good_text = getattr(Storage, mode)[unit]
                        break

                if good_text:
                    break

        return str(self.dtime.strftime('%Y-%m-%d %H:%M')) + ", " + self.player.nickname + ": " + \
               str(self.prod_value) + ' ' + str(good_text) + " в " + str(self.prod_storage.region.region_name)

    # Свойства класса
    class Meta:
        verbose_name = "Лог производства"
        verbose_name_plural = "Логи производства"
