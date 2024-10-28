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

        from player.logs.print_log import log

        if self.points >= 350 > self.paid_points:
            self.paid_points = 350
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

        elif self.points >= 700 > self.paid_points:
            self.paid_points = 700
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

        elif self.points >= 1050 > self.paid_points:
            self.paid_points = 1050
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

        elif self.points >= 1400 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 1400

        elif self.points >= 1750 > self.paid_points:
            log('+1750')
            self.paid_points = 1750
            if self.player.premium < timezone.now():
                log('+1750=2')
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                log('+1750=3')
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

        elif self.points >= 2100 > self.paid_points:
            self.paid_points = 2100
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

        elif self.points >= 2450 > self.paid_points:
            self.paid_points = 2450
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

        elif self.points >= 2800 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 2800

        elif self.points >= 3150 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 3150

        elif self.points >= 3500 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 3500

        elif self.points >= 3850 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 3850

        elif self.points >= 4200 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 4200

    def __str__(self):
        return self.player.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Участник ивента"
        verbose_name_plural = "Участники ивента"
