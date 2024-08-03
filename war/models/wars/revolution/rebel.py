# coding=utf-8
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy

from player.actual_manager import ActualManager
from player.player import Player
from region.models.region import Region
from storage.models.good import Good


# повстанец (человек, оплативший начало восстания в регионе)
class Rebel(models.Model):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей.

    # регион
    region = models.ForeignKey(Region, verbose_name='Регион', on_delete=models.CASCADE, related_name="rebel_region")

    # игрок
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='Игрок', related_name="rebel_player")

    # признак того что повстанец был с пропиской
    resident = models.BooleanField(default=False, verbose_name='С пропиской')

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    # дата создания записи
    dtime = models.DateTimeField(default=timezone.now, blank=True,
                                 verbose_name='Время создания записи')

    def __str__(self):
        return f"Повстанец {self.player.nickname} в регионе {self.region.region_name}"

    # Свойства класса
    class Meta:
        verbose_name = "Повстанец"
        verbose_name_plural = "Повстанцы"
