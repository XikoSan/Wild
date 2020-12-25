import datetime
from django.db import models

from party.party import Party
from player.player import Player


# Заявка на вступление в партию
# player - игрок, вступающий в партию
# party - партия, куда подают заявку
class PartyApply(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='Кандидат')
    party = models.ForeignKey(Party, on_delete=models.CASCADE, verbose_name='Партия вступления')

    def __str__(self):
        return self.party.title + "_" + self.player.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Заявка в партию"
        verbose_name_plural = "Заявки в партии"
