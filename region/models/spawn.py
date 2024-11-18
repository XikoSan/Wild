# coding=utf-8
import math

from django.db import models
from region.models.region import Region

# Определяет список регионов, в которых игрок из конкретной страны может появиться
class Spawn(models.Model):
    # Код страны
    # смотри тут:
    # https://github.com/AndiDittrich/GeoIP-Country-Lists/blob/master/GeoLite2/GeoLite2-Country-CSV_20150407/GeoLite2-Country-Locations-ru.csv
    code = models.CharField(max_length=2, default='', verbose_name='Код страны')

    # регионы
    regions = models.ManyToManyField(Region, blank=True,
                                       related_name='regions',
                                       verbose_name='Регионы')

    def __str__(self):
        return self.code

    # Свойства класса
    class Meta:
        verbose_name = "Спавн"
        verbose_name_plural = "Спавны"
