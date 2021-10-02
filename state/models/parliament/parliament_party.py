# coding=utf-8
# import datetime
# import sys
# from PIL import Image
# from datetime import timedelta
# from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
# from io import BytesIO
from django.core.validators import MinValueValidator, MaxValueValidator

from party.party import Party
from state.models.parliament.parliament import Parliament


# класс, указывающий какой процент парламента занимает партия
# parliament - парламент, который занимает партия
# party - партия парламента
# количество мест в парламенте, занимаемое партией
class ParliamentParty(models.Model):
    parliament = models.ForeignKey(Parliament, on_delete=models.CASCADE, verbose_name='Парламент')

    party = models.OneToOneField(Party, on_delete=models.CASCADE, verbose_name='Партия парламента')

    seats = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return self.parliament.state.title + "_" + self.party.title

    # Свойства класса
    class Meta:
        verbose_name = "Парламентская партия"
        verbose_name_plural = "Парламентские партии"
