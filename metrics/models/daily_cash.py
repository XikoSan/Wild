# coding=utf-8

from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from player.actual_manager import ActualManager
from regime.regime import Regime

# заработанные за указанные сутки деньги
class DailyCash(models.Model):

    # день
    date = models.DateField(default=timezone.now)

    # запасы денег
    cash = models.BigIntegerField(default=0, verbose_name='Добыто денег')

    def __str__(self):
        return self.date.strftime("%d/%m/%Y")

    # Свойства класса
    class Meta:
        verbose_name = "Заработок за день"
        verbose_name_plural = "Заработок за день"
