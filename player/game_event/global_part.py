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

        Lootbox = apps.get_model('player.Lootbox')

        if self.points >= 6600000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 25000:
                if Lootbox.objects.filter(player=char_part.player).exists():
                    lbox = Lootbox.objects.get(player=char_part.player)
                else:
                    lbox = Lootbox(player=char_part.player)

                lbox.stock += 1
                lbox.save()

                char_part.global_paid_points = 6600000

        if self.points >= 13200000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 50000:
                if Lootbox.objects.filter(player=char_part.player).exists():
                    lbox = Lootbox.objects.get(player=char_part.player)
                else:
                    lbox = Lootbox(player=char_part.player)

                lbox.stock += 1
                lbox.save()

                char_part.global_paid_points = 13200000

        if self.points >= 19800000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 75000:
                if Lootbox.objects.filter(player=char_part.player).exists():
                    lbox = Lootbox.objects.get(player=char_part.player)
                else:
                    lbox = Lootbox(player=char_part.player)

                lbox.stock += 1
                lbox.save()

                char_part.global_paid_points = 19800000

        if self.points >= 26400000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 100000:
                if char_part.boost < 40:
                    char_part.boost = 40

                char_part.global_paid_points = 26400000

        if self.points >= 33000000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 125000:
                if char_part.boost < 45:
                    char_part.boost = 45

                char_part.global_paid_points = 33000000

        if self.points >= 39600000 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 150000:
                if char_part.boost < 50:
                    char_part.boost = 50

                char_part.global_paid_points = 39600000

        return char_part

    def __str__(self):
        return self.event.title

    # Свойства класса
    class Meta:
        verbose_name = "Общий счет ивента"
        verbose_name_plural = "Общие счета ивента"
