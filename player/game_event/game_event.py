# coding=utf-8

import datetime
import json

from django.db import models
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask

from player.player import Player
from state.models.parliament.parliament import Parliament


# Игровой ивент
class GameEvent(models.Model):
    # признак того что законопроект рассматривается сейчас
    running = models.BooleanField(default=False, verbose_name='Включен')

    # название
    title = models.CharField(max_length=30, blank=False, verbose_name='Никнейм')

    # время начала ивента - если включен
    event_start = models.DateTimeField(default=timezone.now(), blank=True,
                                        verbose_name='Время начала')

    event_end = models.DateTimeField(default=timezone.now() + datetime.timedelta(days=7), blank=True, null=True,
                                      verbose_name='Время завершения')

    def __str__(self):
        return self.title

    # Указание абстрактности класса
    class Meta:
        verbose_name = "Ивент"
        verbose_name_plural = "Ивенты"
