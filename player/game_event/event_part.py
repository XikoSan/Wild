import datetime
from django.apps import apps
from django.db import models
from django.db.models import F
from django.utils import timezone

from ava_border.models.ava_border import AvaBorder
from ava_border.models.ava_border_ownership import AvaBorderOwnership
from player.game_event.game_event import GameEvent
from player.lootbox.lootbox import Lootbox
from player.player import Player
from region.models.plane import Plane


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

    # буст к Финансированию в процентах
    boost = models.IntegerField(default=0, verbose_name='Бонус к дейлику')

    # очков события
    paid_points = models.IntegerField(default=0, verbose_name='Последний оплаченный этап')

    # очков события
    global_paid_points = models.IntegerField(default=0, verbose_name='Глобальный оплаченный этап')

    def prize_check(self):

        if self.points >= 2450 > self.paid_points:
            self.paid_points = 2450
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

        elif self.points >= 4900 > self.paid_points:
            self.paid_points = 4900
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

        elif self.points >= 7350 > self.paid_points:
            self.paid_points = 7350
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

        elif self.points >= 9800 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 9800

        elif self.points >= 12250 > self.paid_points:
            self.paid_points = 12250
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

        elif self.points >= 14700 > self.paid_points:
            self.paid_points = 14700
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

        elif self.points >= 17150 > self.paid_points:
            self.paid_points = 17150
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

        elif self.points >= 19600 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 19600

        elif self.points >= 22050 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 22050

        elif self.points >= 24500 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 24500

        elif self.points >= 26950 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=4))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=4))

            self.paid_points = 26950

        elif self.points >= 29400 > self.paid_points:
            plane = Plane(player=self.player, plane='trickster', color='friday')
            plane.save()

            self.paid_points = 29400

    def __str__(self):
        return self.player.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Участник ивента"
        verbose_name_plural = "Участники ивента"
