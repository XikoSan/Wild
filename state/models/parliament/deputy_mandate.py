# coding=utf-8
# import datetime
# import sys
# from PIL import Image
# from datetime import timedelta
# from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
# from io import BytesIO

from party.party import Party
from player.player import Player
from state.models.parliament.parliament import Parliament


# класс, указывающий право участвовать в деятельности парламента государства от имени партии
class DeputyMandate(models.Model):
    # партия, от которой избран
    party = models.ForeignKey(Party, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Представляет партию')
    # игрок - депутат
    player = models.OneToOneField(Player, default=None, null=True, on_delete=models.SET_NULL, blank=True, verbose_name='Депутат')
    # парламент, в котороый избран
    parliament = models.ForeignKey(Parliament, on_delete=models.CASCADE, verbose_name='Заседает в парламенте')
    # Президентский мандат - партия не указывается
    is_president = models.BooleanField(default=False, null=False, verbose_name='Президентский')

    def __str__(self):
        if self.player:
            return self.player.nickname + "_" + self.parliament.state.title
        else:
            return 'ПУСТО' + "_" + self.parliament.state.title

    # Свойства класса
    class Meta:
        verbose_name = "Мандат"
        verbose_name_plural = "Мандаты"
