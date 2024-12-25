# coding=utf-8
import datetime
from django.db import models
from django.utils.translation import gettext_lazy
from django.utils.translation import ugettext as _

from player.player import Player


# Количество лутбоксов у игрока
class Lootbox(models.Model):
    # склад
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='Игрок')

    # количество
    stock = models.IntegerField(default=0, verbose_name='Число сундуков')
    # количество до гаранта
    garant_in = models.IntegerField(default=100, verbose_name='До гаранта')

    # количество
    opened = models.IntegerField(default=0, verbose_name='Открыто сундуков')

    def __str__(self):
        return str(self.stock) + ' сундуков ' + self.player.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Лутбоксы"
        verbose_name_plural = "Лутбоксы"
