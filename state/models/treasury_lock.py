# coding=utf-8
from django.db import models

from player.actual_manager import ActualManager
from storage.models.storage import Storage
from state.models.treasury import Treasury
from storage.models.good import Good


# Блокировки ресурсов в Казне
class TreasuryLock(models.Model):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей

    # склад блокировки
    lock_treasury = models.ForeignKey(Treasury, default=None, on_delete=models.CASCADE,
                                      verbose_name='Казна', related_name="lock_treasury")

    # блокируемый товар
    lock_good = models.ForeignKey(Good, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Товар')

    # признак блокированных денег вместо товара
    cash = models.BooleanField(default=False, verbose_name='Наличные')

    lock_count = models.BigIntegerField(default=0, verbose_name='Количество')

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    def __str__(self):
        return 'Блокировка Казны'

    # Свойства класса
    class Meta:
        verbose_name = "Блокировка Казны"
        verbose_name_plural = "Блокировки Казны"
