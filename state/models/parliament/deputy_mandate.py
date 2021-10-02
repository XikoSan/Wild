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
    # игрок - депутат
    player = models.OneToOneField(Player, on_delete=models.CASCADE, verbose_name='Депутат')
    # партия, от которой избран
    party = models.ForeignKey(Party, on_delete=models.CASCADE, verbose_name='Представляет партию')
    # парламент, в котороый избран
    parliament = models.ForeignKey(Parliament, on_delete=models.CASCADE, verbose_name='Заседает в парламенте')

    def __str__(self):
        return self.player.nickname + "_" + self.parliament.state.title

    # Свойства класса
    class Meta:
        verbose_name = "Мандат"
        verbose_name_plural = "Мандаты"
