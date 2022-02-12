from django.db import models

from chat.models.sticker_pack import StickerPack
from player.actual_manager import ActualManager


class Sticker(models.Model):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей.

    # набор стикеров
    pack = models.ForeignKey(StickerPack, on_delete=models.CASCADE, blank=False,
                             verbose_name='Стикерпак', related_name="sticker_pack")

    # описание стикера
    description = models.CharField(max_length=20, blank=False, verbose_name='Описание стикера')

    # картинка стикера
    image = models.ImageField(upload_to='img/stickers/', blank=False, verbose_name='Стикер')

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    def __str__(self):
        return self.description

    # Свойства класса
    class Meta:
        verbose_name = "Стикер"
        verbose_name_plural = "Стикеры"
