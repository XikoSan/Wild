# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy

from region.region import Region
from state.models.state import State


class Capital(models.Model):
    # государство принадлежности
    state = models.OneToOneField(State, on_delete=models.CASCADE, verbose_name='Государство',
                                 related_name="cap_state")
    # регион размещения
    region = models.ForeignKey(Region, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                               verbose_name='Регион размещения', related_name="capital_placement")

    def __str__(self):
        return self.state.title

    # Свойства класса
    class Meta:
        verbose_name = "Столица"
        verbose_name_plural = "Столицы"
