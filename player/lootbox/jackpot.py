# coding=utf-8
import datetime
from django.db import models
from django.utils.translation import gettext_lazy
from django.utils.translation import ugettext as _

from player.player import Player


# Баланс джекпота
class Jackpot(models.Model):

    # количество
    amount = models.IntegerField(default=0, verbose_name='количество')

    def __str__(self):
        return f'Джекпот в размере {self.amount}'

    # Свойства класса
    class Meta:
        verbose_name = "Джекпот"
        verbose_name_plural = "Джекпоты"
