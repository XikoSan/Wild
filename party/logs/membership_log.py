# coding=utf-8
from datetime import datetime
from django.db import models

from party.party import Party
from player.logs.log import Log


# Лог партийной активности игрока
class MembershipLog(Log):
    # партия, в которой игрок состоял
    party = models.ForeignKey(Party, default=None, null=False, on_delete=models.CASCADE, blank=True,
                              verbose_name='Партия-Автор', related_name="member_of_party")

    # дата выхода из партии
    exit_dtime = models.DateTimeField(default=None, null=True, blank=True,
                                      verbose_name='Время выхода из партии')

    def __str__(self):
        if self.exit_dtime:
            return self.player.nickname + " в партии " + self.party.title + " с " + str(
                self.dtime.strftime('%Y-%m-%d %H:%M')) + " по " + str(self.exit_dtime.strftime('%Y-%m-%d %H:%M'))
        else:
            return self.player.nickname + " в партии " + self.party.title + " с " + str(
                self.dtime.strftime('%Y-%m-%d %H:%M'))

    # Свойства класса
    class Meta:
        verbose_name = "Лог партийной активности"
        verbose_name_plural = "Логи партийной активности"
