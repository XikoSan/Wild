# coding=utf-8

from django.db import models

from player.player import Player
from polls.models.poll import Poll


# вариант ответа на опрос
class Variant(models.Model):
    # опрос
    poll = models.ForeignKey(Poll, default=None, null=True, on_delete=models.CASCADE, verbose_name='Опрос',
                             related_name="poll")

    # Текст варианта
    text = models.CharField(max_length=100, blank=False, verbose_name='Вариант опроса')

    # голоса "за"
    votes_pro = models.ManyToManyField(Player, blank=True,
                                       related_name='poll_votes_pro',
                                       verbose_name='Голоса "за"')

    def __str__(self):
        return str(self.text)

    # Свойства класса
    class Meta:
        verbose_name = "Вариант опроса"
        verbose_name_plural = "Варианты опросов"
