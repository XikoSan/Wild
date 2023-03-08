# coding=utf-8

from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from player.actual_manager import ActualManager

# добытая за указанные сутки руда
class DailyOre(models.Model):

    # день
    date = models.DateField(default=timezone.now)

    # запасы
    ore = models.BigIntegerField(default=0, verbose_name='Добыто руды')

    ore_type_choices = (
        ('coal', 'Уголь'),
        ('iron', 'Железо'),
        ('bauxite', 'Бокситы'),
    )

    type = models.CharField(
        max_length=7,
        choices=ore_type_choices,
        default='coal',
    )

    def __str__(self):
        return self.date.strftime("%d/%m/%Y")

    # Свойства класса
    class Meta:
        verbose_name = "Руд за день"
        verbose_name_plural = "Руд за день"
