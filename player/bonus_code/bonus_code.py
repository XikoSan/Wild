from django.contrib.humanize.templatetags.humanize import number_format
from django.db import models
from django.utils import timezone

from player.player import Player


# бонус - код
class BonusCode(models.Model):
    # код
    code = models.CharField(max_length=30, blank=False, verbose_name='Бонус-код')

    # многоразовый код
    reusable = models.BooleanField(default=False, null=False, verbose_name='Многоразовый')

    # дата истечения кода
    date = models.DateTimeField(default=timezone.now, verbose_name='Дата истечения кода')

    # бонус: премиум-дни
    premium = models.IntegerField(default=0, verbose_name='Дни премиума')
    # бонус: золото
    gold = models.IntegerField(default=0, verbose_name='Золото')
    # бонус: Wild Pass
    wild_pass = models.IntegerField(default=0, verbose_name='Wild Pass')
    # бонус: деньги
    cash = models.IntegerField(default=0, verbose_name='Деньги')

    def __str__(self):
        ret = 'Код: '

        if self.premium:
            ret += f'{self.premium} дней'

        if self.gold:
            if ret:
                ret += ', '
            ret += f'{self.gold} золота'

        if self.wild_pass:
            if ret:
                ret += ', '
            ret += f'{self.wild_pass} WP'

        if self.cash:
            if ret:
                ret += ', '
            ret += f'{number_format(self.cash)} $'

        return ret

    # Свойства класса
    class Meta:
        verbose_name = "Бонус-код"
        verbose_name_plural = "Бонус-коды"
