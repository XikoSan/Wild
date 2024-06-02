# coding=utf-8
from django import forms
from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy, pgettext_lazy, ugettext as _

from player.player import Player


# Соавторы контента лутбоксов, которым полагается комиссия
class LootboxCoauthor(models.Model):
    # со-автор
    player = models.ForeignKey(Player, default=None, null=True, on_delete=models.CASCADE, verbose_name='Со-автор')

    # комиссия соавтора:
    percent = models.DecimalField(default=00.00, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                  max_digits=5, decimal_places=2, verbose_name='Комиссия соавтора')

    def __str__(self):
        return f'Комиссия соавтора {self.player.nickname}: {self.percent}%'

    # Свойства класса
    class Meta:
        verbose_name = "Комиссия соавтора"
        verbose_name_plural = "Комиссия соавторов"
