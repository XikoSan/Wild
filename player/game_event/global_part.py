import datetime
from django.apps import apps
from django.db import models
from django.db.models import F
from django.utils import timezone

from ava_border.models.ava_border import AvaBorder
from ava_border.models.ava_border_ownership import AvaBorderOwnership
from player.game_event.game_event import GameEvent
from player.player import Player


# общий счет ивента
class GlobalPart(models.Model):
    # ивент
    event = models.ForeignKey(GameEvent, on_delete=models.CASCADE, blank=False,
                              verbose_name='Ивент')

    # очков события
    points = models.IntegerField(default=0, verbose_name='Очков события')

    def prize_check(self, char_part):

        if self.points >= 96000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 700:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 200)

                char_part.global_paid_points = 96000

        if self.points >= 192000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 1400:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 200)

                char_part.global_paid_points = 192000

        if self.points >= 288000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 2100:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 200)

                char_part.global_paid_points = 288000

        if self.points >= 384000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 2800:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 200)

                char_part.global_paid_points = 384000

        if self.points >= 480000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 3500:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 200)

                char_part.global_paid_points = 480000

        if self.points >= 576000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 4200:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 200)

                char_part.global_paid_points = 576000

        return char_part

    def __str__(self):
        return self.event.title

    # Свойства класса
    class Meta:
        verbose_name = "Общий счет ивента"
        verbose_name_plural = "Общие счета ивента"
