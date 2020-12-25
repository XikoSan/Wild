import datetime
from django.db import models

from party.party import Party
from player.player import Player


# класс, указывающий лидера праймериз
# leader - игрок, выйгравший праймериз
# party - партия парламента
class PrimariesLeader(models.Model):
    party = models.OneToOneField(Party, on_delete=models.CASCADE, verbose_name='Лидер в партии')

    leader = models.OneToOneField(Player, on_delete=models.CASCADE, verbose_name='Лидер праймериз')

    def __str__(self):
        return self.leader.nickname + "_" + self.party.title

    # Свойства класса
    class Meta:
        verbose_name = "Лидер праймериз"
        verbose_name_plural = "Лидеры праймериз"
