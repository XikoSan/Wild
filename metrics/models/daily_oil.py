# coding=utf-8

from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from player.actual_manager import ActualManager
from region.region import Region

# добытая за указанные сутки нефть
class DailyOil(models.Model):

    # день
    date = models.DateField(default=timezone.now)

    # запасы
    oil = models.BigIntegerField(default=0, verbose_name='Добыто нефти')

    type = models.CharField(
        max_length=10,
        choices=Region.oil_type_choices,
        default='urals_oil',
    )

    def __str__(self):
        return self.date.strftime("%d/%m/%Y")

    # Свойства класса
    class Meta:
        verbose_name = "Нефти за день"
        verbose_name_plural = "Нефти за день"
