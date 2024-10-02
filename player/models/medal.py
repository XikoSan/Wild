# coding=utf-8
from django import forms
from django.apps import apps
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy, pgettext_lazy, ugettext as _

from player.player import Player


# Владелец самолёта
class Medal(models.Model):

    # владелец склада
    player = models.ForeignKey(Player, default=None, null=True, on_delete=models.CASCADE, verbose_name='Владелец')

    # количество медалей
    count = models.IntegerField(default=0, verbose_name='Количество медалей')

    # вид награды
    medalTypeChoices = (
        ('year', 'За год игры в WP'),
        ('alpha', 'За альфа-тест WP'),
        ('beta', 'За бета-тест WP'),
        ('public', 'За открытый тест WP'),
    )
    type = models.CharField(
        max_length=10,
        choices=medalTypeChoices,
        default='year',
    )

    def __str__(self):
        return f'{self.count} медалей "{self.get_type_display()}" игрока {self.player.nickname}'

    # Свойства класса
    class Meta:
        verbose_name = "Медаль"
        verbose_name_plural = "Медали"
