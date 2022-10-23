from django.db import models

from player.game_event.game_event import GameEvent
from player.player import Player

# Участник ивента
class EventPart(models.Model):

    # игрок
    player = models.ForeignKey(Player, on_delete=models.CASCADE, blank=False,
                              verbose_name='Игрок')

    # ивент
    event = models.ForeignKey(GameEvent, on_delete=models.CASCADE, blank=False,
                             verbose_name='Рамка')

    # очков события
    points = models.IntegerField(default=0, verbose_name='Очков события')

    def __str__(self):
        return self.player.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Участник ивента"
        verbose_name_plural = "Участники ивента"
