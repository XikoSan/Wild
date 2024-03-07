# coding=utf-8
import datetime
from django.db import models
from django.utils.translation import gettext_lazy
from django.utils.translation import ugettext as _
from storage.models.good import Good
from state.models.treasury import Treasury

# Товар в Казне
class TreasuryStock(models.Model):

    # склад
    treasury = models.ForeignKey(Treasury, on_delete=models.CASCADE, verbose_name='Казна')

    # товар
    good = models.ForeignKey(Good, on_delete=models.CASCADE, verbose_name='Товар')

    # количество
    stock = models.IntegerField(default=0, verbose_name='Запас')

    def __str__(self):
        return str(self.stock) + ' ' + self.good.name

    # Свойства класса
    class Meta:
        verbose_name = "Запас Казны"
        verbose_name_plural = "Запасы Казны"