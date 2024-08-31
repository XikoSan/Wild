# coding=utf-8
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy

from player.logs.log import Log


# запись об начислении премиум-аккаунта
class PremLog(Log):
    # денег передано или получено
    days = models.BigIntegerField(default=0, verbose_name='Дней начислено')

    # текст активности
    activityChoices = (
        ('buying',  'Покупка'),
        ('bonus',  'Бонус-код'),
        ('lootbox', 'Награда из лутбокса'),
        ('wpass', 'Активация Wildpass'),
    )
    activity_txt = models.CharField(
        max_length=7,
        choices=activityChoices,
        blank=True,
        null=True
    )

    def __str__(self):
        return str(self.days) + ' дней премиума за ' + str(self.get_activity_txt_display())

    # Свойства класса
    class Meta:
        verbose_name = "Лог премиума"
        verbose_name_plural = "Логи премиума"
