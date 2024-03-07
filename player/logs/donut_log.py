# coding=utf-8
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy

from player.logs.log import Log


# запись выданной в этом месяце награде VK Donut
# требуется только дата выдачи награды
class DonutLog(Log):

    def __str__(self):
        return str(self.player.nickname) + ' за ' + str(self.dtime.strftime('%Y-%m-%d %H:%M'))

    # Свойства класса
    class Meta:
        verbose_name = "Лог VK Donut"
        verbose_name_plural = "Логи VK Donut"
