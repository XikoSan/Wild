# coding=utf-8
from django.db import models

from player.actual_manager import ActualManager
from storage.models.storage import Storage
from state.models.treasury import Treasury


# Блокировки ресурсов в Казне
class TreasuryLock(models.Model):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей

    # склад блокировки
    lock_treasury = models.ForeignKey(Treasury, default=None, on_delete=models.CASCADE,
                                      verbose_name='Казна', related_name="lock_treasury")

    # блокируемый товар
    choices_list = Storage.get_choises()
    choices_list.insert(0, ('cash', 'Наличные'))

    lock_good = models.CharField(
        max_length=10,
        choices=choices_list,
        default=None,
        verbose_name='Товар',
    )

    lock_count = models.BigIntegerField(default=0, verbose_name='Количество')

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    def __str__(self):
        return 'Блокировка Казны'

    # Свойства класса
    class Meta:
        verbose_name = "Блокировка Казны"
        verbose_name_plural = "Блокировки Казны"
