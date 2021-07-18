# coding=utf-8
from django.db import models
from storage.models.storage import Storage
from player.logs.log import Log


# Лог торговли
class TradingLog(Log):
    # Денег передано:
    # если офффер-продажа - то от игрока в логе к продавцу
    # если оффер-покупка  - то от покупателя к игроку в логе
    cash_value = models.BigIntegerField(default=0, verbose_name='Денег передано')
    # склад принявшего оффер
    player_storage = models.ForeignKey(Storage, default=None, null=True, on_delete=models.CASCADE, blank=True,
                                      verbose_name='Склад принявшего оффер', related_name="player_storage")
    # стоимость доставки
    delivery_value = models.BigIntegerField(default=0, verbose_name='Стоимость доставки')
    # Товаров передано: в противоположную сторону
    good_value = models.BigIntegerField(default=0, verbose_name='Товаров передано')

    def __str__(self):
        return str(self.dtime.strftime('%Y-%m-%d %H:%M')) + ", " + self.player.nickname + ": " + str(
            self.good_value) + " за " + str(self.cash_value)

    # Свойства класса
    class Meta:
        verbose_name = "Лог торговли"
        verbose_name_plural = "Логи торговли"
