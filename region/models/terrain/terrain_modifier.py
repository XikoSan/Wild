# coding=utf-8
import math

from django.db import models
from region.models.terrain.terrain import Terrain
from war.models.wars.unit import Unit

# Модификатор рельефа региона
# влияет на эффективность юнитов в бою
class TerrainModifier(models.Model):
    # регион
    terrain = models.ForeignKey(Terrain, blank=False, on_delete=models.CASCADE,
                              verbose_name='Рельеф')

    unit = models.ForeignKey(Unit, blank=False, on_delete=models.CASCADE,
                              verbose_name='Юнит')

    modifier = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Модификатор')


    def __str__(self):
        return f'{ self.terrain.title }: x{ self.modifier } { self.unit.good.name }'

    # Свойства класса
    class Meta:
        verbose_name = "Модификатор рельефа"
        verbose_name_plural = "Модификаторы рельефа"
