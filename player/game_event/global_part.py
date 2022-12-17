import datetime
from django.db import models
from django.utils import timezone

from ava_border.models.ava_border_ownership import AvaBorderOwnership
from ava_border.models.ava_border import AvaBorder
from player.game_event.game_event import GameEvent
from player.player import Player
from django.db.models import F

# общий счет ивента
class GlobalPart(models.Model):

    # ивент
    event = models.ForeignKey(GameEvent, on_delete=models.CASCADE, blank=False,
                              verbose_name='Ивент')

    # очков события
    points = models.IntegerField(default=0, verbose_name='Очков события')

    def prize_check(self, char_part):

        if self.points >= 300000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 5000:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 1000)

            char_part.global_paid_points = 300000


        if self.points >= 600000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 10000:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 1000)

            char_part.global_paid_points = 600000


        if self.points >= 900000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 15000:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 1000)

            char_part.global_paid_points = 900000


        if self.points >= 1200000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 20000:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 1000)

            char_part.global_paid_points = 1200000


        if self.points >= 1500000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 25000:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 1000)

            char_part.global_paid_points = 1500000


        if self.points >= 1800000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 30000:
                Player.objects.filter(pk=char_part.player.pk).update(cards_count=F('cards_count') + 1)

            char_part.global_paid_points = 1800000


        return char_part


    def __str__(self):
        return self.event.title

    # Свойства класса
    class Meta:
        verbose_name = "Общий счет ивента"
        verbose_name_plural = "Общие счета ивента"
