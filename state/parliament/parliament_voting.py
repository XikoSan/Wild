# coding=utf-8
import datetime
# import sys
# from PIL import Image
# from datetime import timedelta
# from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models

from state.parliament.parliament import Parliament


# from io import BytesIO


# класс выборы
# parliament - парламент, в который проходят выборы
# время начала и конца выборов
class ParliamentVoting(models.Model):
    # признак того что выборы активны
    running = models.BooleanField(default=False, verbose_name='Идут сейчас')
    # парламент, в который происходят выборы
    parliament = models.ForeignKey(Parliament, on_delete=models.CASCADE, verbose_name='Парламент')
    # время начала голосования
    voting_start = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True)
    # время конца голосования
    voting_end = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True)

    def __str__(self):
        return self.parliament.state.title + "_" + self.voting_start.__str__()

    # Свойства класса
    class Meta:
        verbose_name = "Выборы"
        verbose_name_plural = "Выборы"
