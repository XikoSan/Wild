# coding=utf-8
import datetime
from django.db import models
from django.utils.translation import gettext_lazy
from django.utils.translation import ugettext as _
from .good import Good
from storage.models.storage import Storage

# Товар на Складе
class Stock(models.Model):

    # склад
    storage = models.ForeignKey(Storage, default=None, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Склад')

    # товар
    good = models.ForeignKey(Good, on_delete=models.CASCADE, verbose_name='Товар')

    # количество
    stock = models.IntegerField(default=0, verbose_name='Запас')

    def __str__(self):
        return str(self.stock) + ' ' + self.good.name

    # Свойства класса
    class Meta:
        verbose_name = "Запас"
        verbose_name_plural = "Запасы"