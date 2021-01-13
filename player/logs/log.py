# coding=utf-8
import datetime
from datetime import timedelta
from django.db import models
from django.utils import timezone

from player.player import Player


# Абстрактный класс логов
# Позволяет создавать логи разных типов при общей механике
class Log(models.Model):
    # персонаж
    player = models.ForeignKey(Player, default=None, null=True, on_delete=models.CASCADE, verbose_name='Персонаж')
    # дата создания записи
    dtime = models.DateTimeField(default=timezone.now, blank=True,
                                 verbose_name='Время создания записи')

    # Указание абстрактности класса
    class Meta:
        abstract = True
