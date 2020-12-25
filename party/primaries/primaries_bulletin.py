import datetime
from django.db import models

from party.primaries.primaries import Primaries
from player.player import Player


# класс бюллетеня праймериз
# primaries - голосование, к которому относится данный бюллетень
# candidate - партия, за которую был отдан голос
class PrimBulletin(models.Model):
    primaries = models.ForeignKey(Primaries, on_delete=models.CASCADE, verbose_name='Праймериз')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player', verbose_name='Голосовавший')
    candidate = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='candidate', verbose_name='Кандидат')

    def __str__(self):
        return self.primaries.party.title + "_" + self.player.nickname + "_" + self.primaries.prim_start.__str__()

    # Свойства класса
    class Meta:
        verbose_name = "Голос на праймериз"
        verbose_name_plural = "Голоса на праймериз"
