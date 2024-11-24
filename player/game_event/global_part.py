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

        if self.points >= 672000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 4900:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 200)

                char_part.global_paid_points = 672000

        if self.points >= 1344000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 9800:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 200)

                char_part.global_paid_points = 1344000

        if self.points >= 2016000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 14700:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 200)

                char_part.global_paid_points = 2016000

        if self.points >= 2688000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 19600:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 200)

                char_part.global_paid_points = 2688000

        if self.points >= 3360000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 24500:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 200)

                char_part.global_paid_points = 3360000

        if self.points >= 4032000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 29400:
                Player.objects.filter(pk=char_part.player.pk).update(gold=F('gold') + 200)

                char_part.global_paid_points = 4032000

        return char_part

    def __str__(self):
        return self.event.title

    # Свойства класса
    class Meta:
        verbose_name = "Общий счет ивента"
        verbose_name_plural = "Общие счета ивента"
