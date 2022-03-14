# coding=utf-8
# import datetime
# import sys
# from PIL import Image
# from datetime import timedelta
# from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models

from gov.models.presidential_voting import PresidentialVoting
from party.party import Party
from player.player import Player


# from io import BytesIO


# класс бюллетеня президентских выборов
# voting - голосование, к которому относится данный бюллетень
# party - партия, за которую был отдан голос
class Vote(models.Model):
    # выборы, к которым относится данный бюллетень
    voting = models.ForeignKey(PresidentialVoting, on_delete=models.CASCADE, verbose_name='Выборы')
    # проголосовавший игрок
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='Голосовавший')
    # лидер праймериз, за которую отдан голос
    challenger = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='Кандидат', related_name='challenger')

    def __str__(self):
        return self.voting.president.state.title + "_" + self.player.nickname + "_" + self.voting.voting_start.__str__()

    # Свойства класса
    class Meta:
        verbose_name = "Бюллетень президентских выборов"
        verbose_name_plural = "Бюллетени президентских выборов"
