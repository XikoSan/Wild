# coding=utf-8
import math

from django.db import models
from region.region import Region


class MapShape(models.Model):
    # регион
    region = models.ForeignKey(Region, blank=False, on_delete=models.CASCADE,
                              verbose_name='Регион', related_name="reg_map")

    # название региона
    on_map_id = models.CharField(max_length=50, verbose_name='ID на карте')

    shape = models.TextField(default='', verbose_name='Вид на карте')

    # масштаб карты при открытии региона
    zoom = models.IntegerField(default=1, verbose_name='Масштаб карты')

    def __str__(self):
        return self.region.region_name

    # Свойства класса
    class Meta:
        verbose_name = "Контур"
        verbose_name_plural = "Контуры на карте"
