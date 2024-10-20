# coding=utf-8
from django.db import models
from django.utils.translation import pgettext_lazy

from bill.models.bill import Bill
from gov.models.custom_rights.energy_rights import EnergyRights
from gov.models.custom_rights.foreign_rights import ForeignRights
from gov.models.custom_rights.mining_stats import MiningStats
from player.views.get_subclasses import get_subclasses
from state.models.state import State


class MinisterRight(models.Model):
    # тип законопроекта, который можно ускорять
    bill_classes = get_subclasses(Bill)
    # строение
    bill_choises = ()

    for bill_cl in bill_classes:
        bill_choises = bill_choises + ((bill_cl.__name__, bill_cl._meta.verbose_name),)

    bill_choises = bill_choises + (('ForeignRights', pgettext_lazy('new_bill', 'Министр иностранных дел')),)
    bill_choises = bill_choises + (('MiningStats', pgettext_lazy('new_bill', 'Статистика добычи')),)

    right = models.CharField(
        max_length=20,
        choices=bill_choises,
    )

    def __str__(self):
        return self.get_right_display()

    # Свойства класса
    class Meta:
        verbose_name = "Право министра"
        verbose_name_plural = "Права министров"
