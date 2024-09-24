# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy

from player.logs.log import Log


# запись об активности с Андроид-приложения
class TestLog(Log):

    def __str__(self):
        return str(self.player.nickname) + ' от  ' + str(self.dtime)

    # Свойства класса
    class Meta:
        verbose_name = "Лог тестирования"
        verbose_name_plural = "Логи тестирования"
