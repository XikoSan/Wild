import datetime
from django.db import models
from django.utils import timezone

from ava_border.models.ava_border_ownership import AvaBorderOwnership
from ava_border.models.ava_border import AvaBorder
from player.game_event.game_event import GameEvent
from player.player import Player
from django.db.models import F

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

    # очков события
    global_paid_points = models.IntegerField(default=0, verbose_name='Глобальный оплаченный этап')

    def prize_check(self):

        if self.points >= 2500 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 2500

        elif self.points >= 5000 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 5000

        elif self.points >= 7500 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 7500

        elif self.points >= 10000 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            AvaBorderOwnership.objects.filter(owner=self.player,
                               in_use=True,
                               ).update(in_use=False)

            AvaBorderOwnership(in_use=True,
                               owner=self.player,
                               border=AvaBorder.objects.get(pk=8),
                               png_use = True
                               ).save()

            self.paid_points = 10000

        elif self.points >= 12500 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 12500

        elif self.points >= 15000 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 15000

        elif self.points >= 17500 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 17500

        elif self.points >= 20000 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            AvaBorderOwnership.objects.filter(owner=self.player,
                               in_use=True,
                               ).update(in_use=False)

            AvaBorderOwnership(in_use=True,
                               owner=self.player,
                               border=AvaBorder.objects.get(pk=9),
                               png_use = True
                               ).save()

            self.paid_points = 20000

        elif self.points >= 22500 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 22500

        elif self.points >= 25000 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 25000

        elif self.points >= 27500 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 27500

        elif self.points >= 30000 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            AvaBorderOwnership.objects.filter(owner=self.player,
                               in_use=True,
                               ).update(in_use=False)

            AvaBorderOwnership(in_use=True,
                               owner=self.player,
                               border=AvaBorder.objects.get(pk=10),
                               png_use = True
                               ).save()

            self.paid_points = 30000

    def __str__(self):
        return self.player.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Участник ивента"
        verbose_name_plural = "Участники ивента"
