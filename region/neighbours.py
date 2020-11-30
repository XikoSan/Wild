# coding=utf-8
from django.db import models

from region.region import Region


# Связь между двумя регионами: порядок не имеет значения
class Neighbours(models.Model):
    region_1 = models.ForeignKey(Region, default=None, null=True, on_delete=models.CASCADE, blank=False,
                                 verbose_name='Регион 1', related_name="region_1")
    region_2 = models.ForeignKey(Region, default=None, null=True, on_delete=models.CASCADE, blank=False,
                                 verbose_name='Регион 2', related_name="region_2")

    def __str__(self):
        return self.region_1.region_name + ' < - > ' + self.region_2.region_name

    # Свойства класса
    class Meta:
        verbose_name = "Связь регионов"
        verbose_name_plural = "Связи регионов"
