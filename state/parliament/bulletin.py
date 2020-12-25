# coding=utf-8
# import datetime
# import sys
# from PIL import Image
# from datetime import timedelta
# from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models

from party.party import Party
from player.player import Player
from state.parliament.parliament_voting import ParliamentVoting


# from io import BytesIO


# класс бюллетеня
# voting - голосование, к которому относится данный бюллетень
# party - партия, за которую был отдан голос
class Bulletin(models.Model):
    # выборы, к которым относится данный бюллетень
    voting = models.ForeignKey(ParliamentVoting, on_delete=models.CASCADE, verbose_name='Выборы')
    # проголосовавший игрок
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='Голосовавший')
    # партия, за которую отдан голос
    party = models.ForeignKey(Party, on_delete=models.CASCADE, verbose_name='Кандидат')

    def __str__(self):
        return self.voting.parliament.state.title + "_" + self.player.nickname + "_" + self.voting.voting_start.__str__()

    # Свойства класса
    class Meta:
        verbose_name = "Бюллетень"
        verbose_name_plural = "Бюллетени"
