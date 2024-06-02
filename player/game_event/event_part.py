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
        Lootbox = apps.get_model('player.Lootbox')

        if self.points >= 12500 > self.paid_points:
            self.paid_points = 12500
            if self.boost < 5:
                self.boost = 5

        elif self.points >= 25000 > self.paid_points:
            self.paid_points = 25000
            if self.boost < 10:
                self.boost = 10

        elif self.points >= 37500 > self.paid_points:
            self.paid_points = 37500
            if self.boost < 15:
                self.boost = 15

        elif self.points >= 50000 > self.paid_points:
            if Lootbox.objects.filter(player=self.player).exists():
                lbox = Lootbox.objects.get(player=self.player)
            else:
                lbox = Lootbox(player=self.player)

            lbox.stock += 1
            lbox.save()

            self.paid_points = 50000

        elif self.points >= 62500 > self.paid_points:
            self.paid_points = 62500
            if self.boost < 20:
                self.boost = 20

        elif self.points >= 75000 > self.paid_points:
            self.paid_points = 75000
            if self.boost < 25:
                self.boost = 25

        elif self.points >= 87500 > self.paid_points:
            self.paid_points = 87500
            if self.boost < 30:
                self.boost = 30

        elif self.points >= 100000 > self.paid_points:
            if Lootbox.objects.filter(player=self.player).exists():
                lbox = Lootbox.objects.get(player=self.player)
            else:
                lbox = Lootbox(player=self.player)

            lbox.stock += 1
            lbox.save()

            self.paid_points = 100000

        elif self.points >= 112500 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 112500

        elif self.points >= 125000 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 125000

        elif self.points >= 137500 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 137500

        elif self.points >= 150000 > self.paid_points:
            if Lootbox.objects.filter(player=self.player).exists():
                lbox = Lootbox.objects.get(player=self.player)
            else:
                lbox = Lootbox(player=self.player)

            lbox.stock += 1
            lbox.save()

            self.paid_points = 150000

    def __str__(self):
        return self.player.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Участник ивента"
        verbose_name_plural = "Участники ивента"
