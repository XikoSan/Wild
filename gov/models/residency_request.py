# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy, ugettext as _

from player.actual_manager import ActualManager
from player.player import Player
from region.region import Region
from state.models.state import State


class ResidencyRequest(models.Model):
    # персонаж
    char = models.ForeignKey(Player, default=None, null=True, on_delete=models.CASCADE, verbose_name='Персонаж',
                             related_name="char")
    # регион запроса
    region = models.ForeignKey(Region, default=None, null=True, on_delete=models.SET_NULL,
                               verbose_name='Регион запроса',
                               related_name="request_region")

    # государство принадлежности
    state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='Государство',
                              related_name="req_state")

    def __str__(self):
        return self.char.nickname + " в " + self.region.region_name

    # Свойства класса
    class Meta:
        verbose_name = "Запрос прописки"
        verbose_name_plural = "Запросы прописки"
