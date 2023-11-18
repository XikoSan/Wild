# coding=utf-8
import math

from django.db import models
from storage.models.good import Good

# Рельеф региона
# содержит набор модификаторов, влияющих на эффективность юнитов в бою
class Terrain(models.Model):
    # название
    title = models.CharField(max_length=50, default='', verbose_name='Название')

    def __str__(self):
        return self.title

    # Свойства класса
    class Meta:
        verbose_name = "Рельеф"
        verbose_name_plural = "Рельефы"
