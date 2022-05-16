# coding=utf-8

from django.db import models

from gov.models.minister_right import MinisterRight
from player.player import Player
from state.models.state import State


class Minister(models.Model):
    # государство принадлежности
    state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='Государство',
                              related_name="minist_state")

    # название должности
    post_name = models.CharField(max_length=30, default='МИД', blank=False, verbose_name='Название должности')

    # игрок
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='Игрок', related_name="minister")

    # права
    rights = models.ManyToManyField(MinisterRight, blank=True,
                                    related_name='rights',
                                    verbose_name='Права')

    def __str__(self):
        return self.state.title

    # Свойства класса
    class Meta:
        verbose_name = "Министр"
        verbose_name_plural = "Министры"
