# coding=utf-8
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy
from django.utils import timezone
from party.party import Party


# запись об передаче золота партиям
class PartyGoldLog(models.Model):
    # партия
    party = models.ForeignKey(Party, on_delete=models.CASCADE, verbose_name='Партия')
    # дата создания записи
    dtime = models.DateTimeField(default=timezone.now, blank=True,
                                 verbose_name='Время создания записи')
    # денег передано или получено
    gold = models.BigIntegerField(default=0, verbose_name='Золота передано')

    # текст активности
    activityChoices = (
        ('rating',  'Места в рейтинге'),
        ('parl_zp',  'Зарплата парламентским'),

        ('salary',  'Выдача золота'),
    )
    activity_txt = models.CharField(
        max_length=10,
        choices=activityChoices,
        blank=True,
        null=True
    )

    def __str__(self):
        return str(self.gold) + ' за ' + str(self.get_activity_txt_display())

    # Свойства класса
    class Meta:
        verbose_name = "Лог партийного золота"
        verbose_name_plural = "Логи партийного золота"
