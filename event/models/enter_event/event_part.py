import datetime
from django.db import models
from django.utils import timezone
from django.apps import apps
from event.models.enter_event.activity_event import ActivityEvent
from django.db.models import F
from player.player import Player

# Участник ивента
class ActivityEventPart(models.Model):
    Lootbox = apps.get_model('player.Lootbox')

    # игрок
    player = models.ForeignKey(Player, on_delete=models.CASCADE, blank=False,
                               verbose_name='Игрок')

    # ивент
    event = models.ForeignKey(ActivityEvent, on_delete=models.CASCADE, blank=False,
                              verbose_name='Ивент')

    # очков события
    points = models.IntegerField(default=0, verbose_name='Очков события')

    # буст к прокачке в процентах
    boost = models.IntegerField(default=0, verbose_name='Бонус к прокачке')

    # очков события
    paid_points = models.IntegerField(default=0, verbose_name='Последний оплаченный этап')

    # очков события
    global_paid_points = models.IntegerField(default=0, verbose_name='Глобальный оплаченный этап')

    def prize_check(self):

        if self.points >= 3 > self.paid_points:
            self.paid_points = 3
            if self.boost < 5:
                self.boost = 5

        elif self.points >= 6 > self.paid_points:
            self.paid_points = 6
            if self.boost < 10:
                self.boost = 10

        elif self.points >= 9 > self.paid_points:
            self.paid_points = 9
            if self.boost < 15:
                self.boost = 15

        elif self.points >= 12 > self.paid_points:
            if Lootbox.objects.filter(player=self.player).exists():
                lbox = Lootbox.objects.get(player=self.player)
            else:
                lbox = Lootbox(player=self.player)

            lbox.stock += 1
            lbox.save()

            self.paid_points = 12

        elif self.points >= 15 > self.paid_points:
            self.paid_points = 15
            if self.boost < 20:
                self.boost = 20

        elif self.points >= 18 > self.paid_points:
            self.paid_points = 18
            if self.boost < 25:
                self.boost = 25

        elif self.points >= 21 > self.paid_points:
            self.paid_points = 21
            if self.boost < 30:
                self.boost = 30

        elif self.points >= 24 > self.paid_points:
            if Lootbox.objects.filter(player=self.player).exists():
                lbox = Lootbox.objects.get(player=self.player)
            else:
                lbox = Lootbox(player=self.player)

            lbox.stock += 1
            lbox.save()

            self.paid_points = 24

        elif self.points >= 27 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 27

        elif self.points >= 30 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 30

        elif self.points >= 33 > self.paid_points:
            if self.player.premium < timezone.now():
                Player.objects.filter(pk=self.player.pk).update(premium=timezone.now() + datetime.timedelta(days=1))
            else:
                Player.objects.filter(pk=self.player.pk).update(premium=F('premium') + datetime.timedelta(days=1))

            self.paid_points = 33

        elif self.points >= 36 > self.paid_points:
            if Lootbox.objects.filter(player=self.player).exists():
                lbox = Lootbox.objects.get(player=self.player)
            else:
                lbox = Lootbox(player=self.player)

            lbox.stock += 1
            lbox.save()

            self.paid_points = 36

    def __str__(self):
        return self.player.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Участник ивента активностей"
        verbose_name_plural = "Участники ивента активностей"
