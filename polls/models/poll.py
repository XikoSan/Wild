# coding=utf-8

from django.db import models

from player.actual_manager import ActualManager


# опрос
class Poll(models.Model):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей.

    # Заголовок опроса
    header = models.CharField(max_length=100, blank=False, verbose_name='Заголовок опроса')

    # дата опроса
    poll_dtime = models.DateTimeField(default=None, null=True, blank=True, verbose_name='Дата опроса')

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    def __str__(self):
        return str(self.header)

    # Свойства класса
    class Meta:
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"
