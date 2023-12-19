# coding=utf-8
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy

from player.logs.log import Log


# запись об передаче золота
class GoldLog(Log):
    # денег передано или получено
    gold = models.BigIntegerField(default=0, verbose_name='Денег передано')
    # произвольный объект активности, в связи с которой были переданы или получены деньги
    content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(blank=True, null=True)

    activity = GenericForeignKey('content_type', 'object_id')
    # текст активности
    activityChoices = (
        ('reward',  'Бонус за репост'),
        ('donut',  'VK Donut'),
        ('mine',  'Майнинг'),
        ('aumine',  'Авто-майнинг'),
        ('stckow',  'Процент за стикеры'),
        ('bx_gld', 'Золото из лутбокса'),

        ('nick', 'Смена никнейма'),
        ('avatar', 'Смена аватара'),
        ('stick', 'Покупка стикеров'),
        ('energy', 'Энергетики'),
        ('party', 'Новая партия'),
        ('ivent', 'Ивент'),
        ('boxes', 'Покупка лутбокса'),

        # обучение
        ('edu_01', 'Награда за прокачку характеристики'),
        ('edu_02', 'Награда за добытое сырьё'),
        ('edu_03', 'Награда за то, что тяпнул'),
        ('edu_04', 'Награда за длинную лекцию о Складе'),
        ('edu_05', 'Награда за изучение карты'),
    )
    activity_txt = models.CharField(
        max_length=6,
        choices=activityChoices,
        blank=True,
        null=True
    )

    def __str__(self):
        return str(self.gold) + ' за ' + str(self.get_activity_txt_display())

    # Свойства класса
    class Meta:
        verbose_name = "Лог золота"
        verbose_name_plural = "Логи золота"
