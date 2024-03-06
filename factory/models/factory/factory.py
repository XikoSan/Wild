# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy, ugettext as _

from player.actual_manager import ActualStorageManager
from player.player import Player
from region.models.region import Region


# Частная фабрика
class Factory(models.Model):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualStorageManager()  # Менеджер активных записей

    # название фабрики
    title = models.CharField(max_length=30, blank=False, verbose_name='Название')
    # изображение фабрики
    image = models.ImageField(upload_to='img/factories/', blank=True, null=True, verbose_name='Изображение')

    # владелец фабрики
    owner = models.ForeignKey(Player, default=None, null=True, on_delete=models.CASCADE, verbose_name='Владелец')

    # регион размещения
    region = models.ForeignKey(Region, default=None, null=True, on_delete=models.SET_NULL,
                               verbose_name='Регион размещения',
                               related_name="factory_place")

    # уровень прокачки. 1 - только пострен
    level = models.IntegerField(default=1, verbose_name=pgettext_lazy('factory', 'Уровень'))

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    def __str__(self):
        return self.title + " в " + self.region.region_name

    # Свойства класса
    class Meta:
        verbose_name = "Фабрика"
        verbose_name_plural = "Фабрики"
