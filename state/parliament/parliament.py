# coding=utf-8
from PIL import Image
from datetime import timedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from io import BytesIO

from party.party import Party
from player.player import Player
from state.state import State


class Parliament(models.Model):
    # размер парламента, мест
    size = models.IntegerField(default=10, validators=[MinValueValidator(10)])
    # государство принадлежности
    state = models.OneToOneField(State, on_delete=models.CASCADE, verbose_name='Государство', related_name="state")

    def __str__(self):
        return self.state.title

    # Свойства класса
    class Meta:
        verbose_name = "Парламент"
        verbose_name_plural = "Парламенты"
