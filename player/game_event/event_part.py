import datetime
from django.db import models
from django.utils import timezone

from ava_border.models.ava_border_ownership import AvaBorderOwnership
from ava_border.models.ava_border import AvaBorder
from player.game_event.game_event import GameEvent
from player.player import Player


# Участник ивента
class EventPart(models.Model):
    # игрок
    player = models.ForeignKey(Player, on_delete=models.CASCADE, blank=False,
                               verbose_name='Игрок')

    # ивент
    event = models.ForeignKey(GameEvent, on_delete=models.CASCADE, blank=False,
                              verbose_name='Ивент')

    # очков события
    points = models.IntegerField(default=0, verbose_name='Очков события')

    # очков события
    paid_points = models.IntegerField(default=0, verbose_name='Последний оплаченный этап')

    def prize_check(self):

        if self.points >= 2000 > self.paid_points:
            if self.player.premium < timezone.now():
                self.player.premium = timezone.now() + datetime.timedelta(days=1)
            else:
                self.player.premium += datetime.timedelta(days=1)

            self.paid_points = 2000

        elif self.points >= 4000 > self.paid_points:
            if self.player.premium < timezone.now():
                self.player.premium = timezone.now() + datetime.timedelta(days=1)
            else:
                self.player.premium += datetime.timedelta(days=1)

            if not AvaBorderOwnership.objects.filter(owner=self.player,
                               border=AvaBorder.objects.get(pk=2)
                               ).exists() or\
                    not AvaBorderOwnership.objects.filter(owner=self.player,
                               border=AvaBorder.objects.get(pk=3)
                               ).exists():

                AvaBorderOwnership(in_use=True,
                                   owner=self.player,
                                   border=AvaBorder.objects.get(pk=1)
                                   ).save()

            self.paid_points = 4000

        elif self.points >= 6000 > self.paid_points:
            if self.player.premium < timezone.now():
                self.player.premium = timezone.now() + datetime.timedelta(days=1)
            else:
                self.player.premium += datetime.timedelta(days=1)

            self.paid_points = 6000

        elif self.points >= 8000 > self.paid_points:
            if self.player.premium < timezone.now():
                self.player.premium = timezone.now() + datetime.timedelta(days=1)
            else:
                self.player.premium += datetime.timedelta(days=1)

            self.paid_points = 8000

        elif self.points >= 10000 > self.paid_points:
            if self.player.premium < timezone.now():
                self.player.premium = timezone.now() + datetime.timedelta(days=1)
            else:
                self.player.premium += datetime.timedelta(days=1)

            if not AvaBorderOwnership.objects.filter(
                               owner=self.player,
                               border=AvaBorder.objects.get(pk=3)
                               ).exists():

                AvaBorderOwnership.objects.filter(owner=self.player).update(in_use=False)

                AvaBorderOwnership(in_use=True,
                                   owner=self.player,
                                   border=AvaBorder.objects.get(pk=2)
                                   ).save()

            self.paid_points = 10000

        elif self.points >= 12000 > self.paid_points:
            if self.player.premium < timezone.now():
                self.player.premium = timezone.now() + datetime.timedelta(days=1)
            else:
                self.player.premium += datetime.timedelta(days=1)

            self.paid_points = 12000

        elif self.points >= 14000 > self.paid_points:
            if self.player.premium < timezone.now():
                self.player.premium = timezone.now() + datetime.timedelta(days=1)
            else:
                self.player.premium += datetime.timedelta(days=1)

            AvaBorderOwnership.objects.filter(owner=self.player).update(in_use=False)

            AvaBorderOwnership(in_use=True,
                               owner=self.player,
                               border=AvaBorder.objects.get(pk=3)
                               ).save()

            self.paid_points = 14000

        self.player.save()

    def __str__(self):
        return self.player.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Участник ивента"
        verbose_name_plural = "Участники ивента"
