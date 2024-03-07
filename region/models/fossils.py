# coding=utf-8
import math

from django.db import models
from region.models.region import Region
from storage.models.good import Good

# Ископаемые руды
# Товар - процент добычи
# Обычно - уголь, железо, бокситы
class Fossils(models.Model):
    # регион
    region = models.ForeignKey(Region, blank=False, on_delete=models.CASCADE,
                              verbose_name='Регион')

    # руда
    good = models.ForeignKey(Good, default=None, on_delete=models.CASCADE, verbose_name='Руда')

    # добываемый процент
    percent = models.IntegerField(default=25, verbose_name='Процент')

    def __str__(self):
        return self.region.region_name + ': ' + str(self.percent) + '% ' + self.good.name

    # Свойства класса
    class Meta:
        verbose_name = "Ископаемое"
        verbose_name_plural = "Ископаемые"
