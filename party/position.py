# coding=utf-8
import sys
from django.db import models

from party.party import Party


class PartyPosition(models.Model):
    # название должности
    title = models.CharField(max_length=255, verbose_name='Название')
    # партия, в которой была создана должность
    party = models.ForeignKey(Party, default=None, null=False, on_delete=models.CASCADE, blank=True,
                              verbose_name='Партия-Автор', related_name="pos_of_party")

    # --- Права --- #
    # базовая должность. Создаётся при объявлении партии, не может быть удалена вручную
    based = models.BooleanField(default=False, verbose_name='Неудаляемая должность')
    # глава партии. Может быть только в одной должности
    party_lead = models.BooleanField(default=False, verbose_name='Лидер партии')
    # признак того, что игрок является секретарём в партии, в которой состоит
    party_sec = models.BooleanField(default=False, verbose_name='Секретарь партии')

    # сохранение
    def save(self):
        super(PartyPosition, self).save()

    def __str__(self):
        return self.title + "_" + self.party.title

    # Свойства класса
    class Meta:
        verbose_name = "Пост в партии"
        verbose_name_plural = "Посты в партиях"
