import datetime
from django.db import models
from django.utils import timezone

from player.player import Player
import random
from django.db.models import F
from player.logs.gold_log import GoldLog

# Траты энергии (по различным условиям)
class EnergySpent(models.Model):
    # игрок
    player = models.ForeignKey(Player, on_delete=models.CASCADE, blank=False,
                               verbose_name='Игрок')

    # очков события
    points = models.IntegerField(default=0, verbose_name='Энергии потрачено')

    # Показатель того, что награда получена
    fin = models.BooleanField(default=False, null=False, verbose_name='Награда выдана')

    def claim_reward(self):
        if self.points >= 1000 and not self.fin:

            sum = random.choices([5, 10, 50, 100, 500, 1000, 5000, 10000,], weights=[30, 25, 15, 12, 8, 5, 3, 2,])
            sum = sum[0]

            Player.objects.filter(pk=self.player.pk).update(gold=F('gold') + sum)
            gold_log = GoldLog(player=self.player, gold=sum, activity_txt='ivent')
            gold_log.save()

            self.fin = True
            self.save()

            return sum

        else:
            self.save()
            return None

    def __str__(self):
        return self.player.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Очки события"
        verbose_name_plural = "Очки мини-событий"
