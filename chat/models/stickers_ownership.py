from django.db import models

from chat.models.sticker_pack import StickerPack
from player.player import Player


class StickersOwnership(models.Model):
    # набор стикеров
    owner = models.ForeignKey(Player, on_delete=models.CASCADE, blank=False,
                              verbose_name='Игрок')

    # набор стикеров
    pack = models.ForeignKey(StickerPack, on_delete=models.CASCADE, blank=False,
                             verbose_name='Стикерпак')

    def __str__(self):
        return self.pack.title

    # Свойства класса
    class Meta:
        verbose_name = "Владелец стикеров"
        verbose_name_plural = "Владельцы стикеров"
