# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy

from player.logs.log import Log


# запись об активности с Андроид-приложения
class TestPointUsage(Log):

    # на что потратили
    buyTypeChoices = (
        ('7_prem', '7 дней према'),
        ('7_prem_2', '7 дней према (2)'),
        ('plane', 'Самолёт'),
        ('cash', 'Деньги'),
        ('gold', 'Золото'),
        ('gold_100_1', 'Золото 100'),
        ('gold_100_2', 'Золото 100 (2)'),
        ('wildpass', 'Wild Pass'),
        ('30_prem', '30 дней према'),
    )
    type = models.CharField(
        max_length=10,
        choices=buyTypeChoices,
        default='7_prem',
    )

    # Очки
    count = models.IntegerField(default=0, verbose_name='Очки')

    def __str__(self):
        return str(self.player.nickname) + ' от  ' + str(self.dtime)

    # Свойства класса
    class Meta:
        verbose_name = "Траты очков тестирования"
        verbose_name_plural = "Траты очков тестирования"
