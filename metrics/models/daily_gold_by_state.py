# coding=utf-8

from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from player.actual_manager import ActualManager
from regime.regime import Regime
from state.models.state import State


# накопанное за указанные сутки золото по государствам
class DailyGoldByState(models.Model):
    # день
    date = models.DateField(default=timezone.now)

    # государство принадлежности
    state = models.OneToOneField(State, on_delete=models.CASCADE, verbose_name='Государство',
                                 related_name="%(class)s_state")

    # добытое золото
    gold = models.BigIntegerField(default=0, verbose_name='Добыто золота')

    def __str__(self):
        return self.date.strftime("%d/%m/%Y")

    # Свойства класса
    class Meta:
        verbose_name = "Золота за день в государстве"
        verbose_name_plural = "Золота за день в государствах"
