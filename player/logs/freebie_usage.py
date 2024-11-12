# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy

from player.logs.log import Log


# запись об активности с Андроид-приложения
class FreebieUsage(Log):

    # на что потратили
    buyTypeChoices = (
        ('gold_500', 'Золото 500'),
        ('cash_500k', 'Деньги 500k'),
    )
    type = models.CharField(
        max_length=10,
        choices=buyTypeChoices,
        default='7_prem',
    )

    def __str__(self):
        return str(self.player.nickname) + ' от  ' + str(self.dtime)

    # Свойства класса
    class Meta:
        verbose_name = "Получение бонуса"
        verbose_name_plural = "Получения бонуса"
