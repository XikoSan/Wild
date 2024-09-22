# coding=utf-8

from django.db import models

from player.actual_manager import ActualManager
from player.player import Player
from modeltranslation.translator import translator, TranslationOptions


class StickerPackTranslation(TranslationOptions):
    fields = ('title', 'creator', 'description',)


# набор стикеров
class StickerPack(models.Model):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей.

    # Название набора
    title = models.CharField(max_length=100, blank=False, verbose_name='Название набора')

    # автор набора
    creator = models.CharField(max_length=100, blank=False, verbose_name='Автор набора')

    # выгодоприобретатель
    owner = models.ForeignKey(Player, default=None, null=True, on_delete=models.SET_NULL, verbose_name='Владелец',
                              related_name="pack_owner")

    # процент за покупку стикера Владельцу
    percent = models.IntegerField(default=50, verbose_name='Процент с продажи')

    # Ссылка на автора набора
    creator_link = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ссылка на автора')

    # Описание набора
    description = models.CharField(max_length=500, blank=True, null=True, verbose_name='Описание набора')

    # Цена набора
    price = models.IntegerField(default=1000, verbose_name='Цена')

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    def __str__(self):
        return str(self.title)

    # Свойства класса
    class Meta:
        verbose_name = "Стикерпак"
        verbose_name_plural = "Стикерпаки"

translator.register(StickerPack, StickerPackTranslation)
