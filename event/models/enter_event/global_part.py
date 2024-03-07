import datetime
from django.apps import apps
from django.db import models
from django.db.models import F
from django.utils import timezone

from event.models.enter_event.activity_event import ActivityEvent
from player.player import Player


# общий счет ивента активности
class ActivityGlobalPart(models.Model):
    # ивент
    event = models.ForeignKey(ActivityEvent, on_delete=models.CASCADE, blank=False,
                              verbose_name='Ивент')

    # очков события
    points = models.IntegerField(default=0, verbose_name='Очков события')

    def prize_check(self, char_part):

        Lootbox = apps.get_model('player.Lootbox')

        if self.points >= 350 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 6:
                if Lootbox.objects.filter(player=char_part.player).exists():
                    lbox = Lootbox.objects.get(player=char_part.player)
                else:
                    lbox = Lootbox(player=char_part.player)

                lbox.stock += 1
                lbox.save()

                char_part.global_paid_points = 350

        if self.points >= 700 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 12:
                if Lootbox.objects.filter(player=char_part.player).exists():
                    lbox = Lootbox.objects.get(player=char_part.player)
                else:
                    lbox = Lootbox(player=char_part.player)

                lbox.stock += 1
                lbox.save()

                char_part.global_paid_points = 700

        if self.points >= 1050 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 18:
                if Lootbox.objects.filter(player=char_part.player).exists():
                    lbox = Lootbox.objects.get(player=char_part.player)
                else:
                    lbox = Lootbox(player=char_part.player)

                lbox.stock += 1
                lbox.save()

                char_part.global_paid_points = 1050

        if self.points >= 1400 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 24:
                if char_part.boost < 40:
                    char_part.boost = 40

                char_part.global_paid_points = 1400

        if self.points >= 1750 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 30:
                if char_part.boost < 45:
                    char_part.boost = 45

                char_part.global_paid_points = 1750

        if self.points >= 2100 > char_part.global_paid_points:

            # если игрок не прошел соотв. этап личной прогрессии - ничего не положено
            if char_part.paid_points >= 36:
                if char_part.boost < 50:
                    char_part.boost = 50

                char_part.global_paid_points = 2100

        return char_part

    def __str__(self):
        return self.event.title

    # Свойства класса
    class Meta:
        verbose_name = "Общий счет ивента активности"
        verbose_name_plural = "Общие счета ивентов активности"
