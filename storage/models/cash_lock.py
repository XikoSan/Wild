# coding=utf-8
import datetime
from django.db import models
from django.utils.translation import gettext_lazy
from django.utils.translation import ugettext as _

from player.player import Player
from storage.models.storage import Storage
from storage.models.trade_offer import TradeOffer

# Блокировки денег на счете игрока, при скупке товаров
class CashLock(models.Model):
    # Счет блокировки
    lock_player = models.ForeignKey(Player, default=None, on_delete=models.CASCADE,
                                    verbose_name='Счет блокировки', related_name="lock_player")

    lock_cash = models.BigIntegerField(default=0, verbose_name='Количество')

    lock_offer = models.ForeignKey(TradeOffer, default=None, on_delete=models.CASCADE,
                                    verbose_name='Торговое предложение', related_name="lock_offer")

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    def __str__(self):
        return self.lock_player.nickname + ': ' + str(self.lock_cash)

    # Свойства класса
    class Meta:
        verbose_name = "Блокировка денег"
        verbose_name_plural = "Блокировки денег"
