# coding=utf-8

from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from player.actual_manager import ActualManager
from regime.regime import Regime

# накопанное за указанные сутки золото
class DailyGold(models.Model):

    # день
    date = models.DateField(default=timezone.now)

    # добытое золото
    gold = models.BigIntegerField(default=0, verbose_name='Добыто золота')

    def __str__(self):
        return self.date.strftime("%d/%m/%Y")

    # Свойства класса
    class Meta:
        verbose_name = "Золота за день"
        verbose_name_plural = "Золота за день"
