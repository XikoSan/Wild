# coding=utf-8
import datetime
from decimal import Decimal
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from math import ceil

from bill.models.explore_all import ExploreAll
from region.models.region import Region


# Разведать ресурсы во всех регионах разом
class ExploreAllRegion(models.Model):
    # регион разведки
    exp_bill = models.ForeignKey(ExploreAll, on_delete=models.CASCADE, verbose_name='Законопроект')
    # регион разведки
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион разведки')
    # объем разведки
    exp_value = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Общий объем разведки')

    # Свойства класса
    class Meta:
        verbose_name = pgettext_lazy('new_bill', "Часть общей разведки")
        verbose_name_plural = pgettext_lazy('new_bill', "Части общей разведки")
