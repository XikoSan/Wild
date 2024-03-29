import datetime
from django.db import models
from django.utils import timezone
from django.apps import apps
from event.models.inviting_event.cash_event import CashEvent
from django.db.models import F
from player.player import Player


# приглашение
class Invite(models.Model):
    # игрок
    sender = models.ForeignKey(Player, on_delete=models.CASCADE, blank=False, related_name='sender',
                               verbose_name='Пригласивший')
    # игрок
    invited = models.ForeignKey(Player, on_delete=models.CASCADE, blank=False, related_name='invited',
                               verbose_name='Приглашённый')

    # очки на старте приглашения
    exp = models.IntegerField(default=0, verbose_name='сумма Характеристик')

    def __str__(self):
        return f"{self.sender.nickname} пригласил {self.invited.nickname}"

    # Свойства класса
    class Meta:
        verbose_name = "Приглашение"
        verbose_name_plural = "Приглашения"
