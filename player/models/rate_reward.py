# coding=utf-8
from django import forms
from django.apps import apps
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy, pgettext_lazy, ugettext as _
from django.utils import timezone
from player.player import Player


# оценившие приложение
class RateReward(models.Model):

    # владелец склада
    player = models.ForeignKey(Player, default=None, null=True, on_delete=models.CASCADE, verbose_name='Владелец')

    nickname = models.CharField(max_length=50, blank=True, verbose_name='Никнейм')

    # дата обновления записи
    dtime = models.DateTimeField(default=timezone.now, blank=True,
                                 verbose_name='Время обновления записи')

    def __str__(self):
        return f'{self.player.nickname} под ником {self.nickname}'

    # Свойства класса
    class Meta:
        verbose_name = "Награды за оценку"
        verbose_name_plural = "Награды за оценку"
