# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy
from storage.models.good import Good


# Юнит - характеристики оружия со Склада
class Unit(models.Model):
    # товар, являющийся оружием
    good = models.ForeignKey(Good, on_delete=models.CASCADE, verbose_name='Товар')

    # Очки урона
    damage = models.IntegerField(default=1, verbose_name='Урон')

    # Затраты энергии за использованную единицу
    energy = models.IntegerField(default=1, verbose_name='Энергии требует')

    def __str__(self):
        return f"{self.good.name}"

    # Свойства класса
    class Meta:
        verbose_name = "Юнит"
        verbose_name_plural = "Юниты"
