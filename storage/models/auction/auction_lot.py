# coding=utf-8
from django.apps import apps
from django.db import models

from player.actual_manager import ActualManager
from player.logs.cash_log import CashLog
from storage.models.auction.auction import BuyAuction
from storage.models.storage import Storage


# Лот аукциона
class AuctionLot(models.Model):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей

    # аукцион
    auction = models.ForeignKey(BuyAuction, default=None, on_delete=models.CASCADE,
                                verbose_name='Аукцион', related_name="auction")

    # количество товара в лоте
    count = models.IntegerField(default=0, verbose_name='Количество в лоте')

    # начальная цена
    start_price = models.IntegerField(default=0, verbose_name='Начальная цена')

    # склад победителя лота
    win_storage = models.ForeignKey(Storage, default=None, null=True, blank=True, on_delete=models.SET_NULL,
                                    verbose_name='Склад победителя', related_name="win_storage")

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    # выполнить лот аукциона
    def run(self):
        # получаем ставку лота
        # если нет ставки - пропускаем
        bet_class = None
        for model in apps.get_models():
            if model.__name__ == 'AuctionBet':
                bet_class = model
                break
        if not bet_class.actual.filter(auction_lot=self).exists():
            # удаляем лот (отметка)
            self.deleted = True
            # сохраняем лот
            self.save()
            return None

        bet = bet_class.actual.get(auction_lot=self)
        # начисляем владельцу ставки на баланс = цена ставки * объем лота
        bet.good_lock.lock_storage.owner.cash += bet.price * self.count
        bet.good_lock.lock_storage.owner.save()
        # логируем
        CashLog(player=bet.good_lock.lock_storage.owner, cash=(bet.price * self.count), activity_txt='auct').save()
        # удаляем блокировку ресурсов из ставки (отметка)
        bet.good_lock.deleted = True
        # сохраняем блокировку
        bet.good_lock.save()

        # прописываем его склад в лоте как победитель
        self.win_storage = bet.good_lock.lock_storage
        # удаляем лот (отметка)
        self.deleted = True
        # сохраняем лот
        self.save()

        return bet.price

    def __str__(self):
        return "Лот аукциона"

    # Свойства класса
    class Meta:
        verbose_name = "Лот аукциона"
        verbose_name_plural = "Лоты аукционов"
