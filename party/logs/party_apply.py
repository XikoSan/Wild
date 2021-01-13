import datetime
from django.db import models
from django.utils import timezone

from party.party import Party
from player.logs.log import Log
from player.player import Player


# Заявка на вступление в партию
# player - игрок, вступающий в партию
# party - партия, куда подают заявку
class PartyApply(Log):
    party = models.ForeignKey(Party, on_delete=models.CASCADE, verbose_name='Партия вступления')
    # тип партии
    open = 'op'
    canceled = 'cs'

    accepted = 'ac'
    rejected = 'rj'
    rejected_all = 'ra'

    apply_choices = (
        (open, 'Новая заявка'),
        (canceled, 'Отозванная заявка'),

        (accepted, 'Одобренная заявка'),
        (rejected, 'Отклонённая заявка'),
        (rejected_all, 'Отклонена с другими'),
    )
    status = models.CharField(
        max_length=2,
        choices=apply_choices,
        default=open,
    )

    def __str__(self):
        return self.party.title + "_" + self.player.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Заявка в партию"
        verbose_name_plural = "Заявки в партии"
