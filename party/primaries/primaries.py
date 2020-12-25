import datetime
from django.db import models

from party.party import Party


# класс праймериз
# parliament - парламент, в который проходят выборы
# время начала и конца выборов
class Primaries(models.Model):
    # признак того что праймериз активны
    running = models.BooleanField(default=False, verbose_name='Идут прямо сейчас')
    # парламент, в который происходят выборы
    party = models.ForeignKey(Party, on_delete=models.CASCADE, verbose_name='Праймериз в партии')
    # время начала голосования
    prim_start = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True)
    # время конца голосования
    prim_end = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True)

    def __str__(self):
        return self.party.title + "_" + self.prim_start.__str__()

    # Свойства класса
    class Meta:
        verbose_name = "Праймериз в партии"
        verbose_name_plural = "Праймериз"
