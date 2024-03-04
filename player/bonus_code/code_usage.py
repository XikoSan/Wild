from django.contrib.humanize.templatetags.humanize import number_format
from django.db import models
from django.utils import timezone

from player.bonus_code.bonus_code import BonusCode
from player.player import Player
from player.logs.log import Log


# список людей, использовавших бонус-коды
class CodeUsage(Log):
    # код
    code = models.ForeignKey(BonusCode, on_delete=models.CASCADE, blank=True, verbose_name='Код')

    def __str__(self):
        return  f'{self.player.nickname} {self.dtime.strftime("%H:%M %d.%m.%y")}'

    # Свойства класса
    class Meta:
        verbose_name = "Использование кодов"
        verbose_name_plural = "Использование кодов"
