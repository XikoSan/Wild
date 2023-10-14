# coding=utf-8
import datetime
from django.conf import settings
from django.db import models
from django.utils import timezone

from player.player import Player
from region.models.region import Region
from state.models.state import State


# Траты игрока в каждом регионе присутствия
class PlayerRegionalExpense(models.Model):
    # персонаж игрока
    player = models.ForeignKey(Player, default=None, on_delete=models.CASCADE, verbose_name='Игрок')

    # регион расходования энергии
    region = models.ForeignKey(Region, default=None, on_delete=models.CASCADE,
                               verbose_name='Регион расходования', related_name="expence_region")

    # расход энергии за эти сутки
    energy_consumption = models.IntegerField(default=0, verbose_name='Расход энергии')

    def get_taxes(self, count):
        # получаем число денег, которое было заработано в этом регионе
        taxed_count = int(self.energy_consumption * count / self.player.energy_consumption)

        if not self.player.account.date_joined + datetime.timedelta(days=7) > timezone.now():
            taxed_count = State.get_taxes(self.region, taxed_count, 'cash', 'cash')

        return taxed_count

    def __str__(self):
        return self.player.nickname + ' в регионе ' + self.region.region_name

    # Свойства класса
    class Meta:
        verbose_name = "Траты энергии игрока"
        verbose_name_plural = "Траты энерии игроков"
