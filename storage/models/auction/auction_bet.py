# coding=utf-8
from django.db import models

from player.actual_manager import ActualManager
from storage.models.auction.auction_lot import AuctionLot
from storage.models.good_lock import GoodLock


# Ставка на аукционе
class AuctionBet(models.Model):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей

    # Лот
    auction_lot = models.ForeignKey(AuctionLot, default=None, on_delete=models.CASCADE,
                                    verbose_name='Лот', related_name="auction_lot")

    # текущая цена
    price = models.IntegerField(default=0, verbose_name='Текущая цена')

    # блокировка склада
    good_lock = models.ForeignKey(GoodLock, default=None, on_delete=models.CASCADE,
                                  verbose_name='Блокировка Склада', related_name="good_lock")

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    def __str__(self):
        return "Ставка аукциона"

    # Свойства класса
    class Meta:
        verbose_name = "Ставка аукциона"
        verbose_name_plural = "Ставки аукционов"
