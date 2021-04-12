import json

import datetime

from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save

from django_celery_beat.models import IntervalSchedule, PeriodicTask

from party.party import Party


schedule = IntervalSchedule.objects.get_or_create(every = 1, period=IntervalSchedule.MINUTES)


# класс праймериз
# parliament - парламент, в который проходят выборы
# время начала и конца выборов
class Primaries(models.Model):
    # признак того что праймериз активны
    running = models.BooleanField(default=False, verbose_name='Идут прямо сейчас')
    # парламент, в который происходят выборы
    party = models.ForeignKey(Party, on_delete=models.CASCADE, verbose_name='Праймериз в партии')
    # время начала голосования
    prim_start = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True, null=True)
    # время конца голосования
    prim_end = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True, null=True)
    # переодическая таска
    task = models.OneToOneField(PeriodicTask, on_delete = models.CASCADE, null = True, blank = True)

    def setup_task(self):
        self.task = PeriodicTask.objects.create(
            name = f'Primaries of {self.party.title} party primaries',
            task = 'finish_primaries',
            interval = IntervalSchedule.objects.get(every=1),
            args = json.dumps([self.party.pk]),
            start_time = timezone.now(),
        )
        self.save()

    def __str__(self):
        return self.party.title + "_" + self.prim_start.__str__()

    # Свойства класса
    class Meta:
        verbose_name = "Праймериз в партии"
        verbose_name_plural = "Праймериз"


@receiver(post_save, sender=Primaries)
def save_post(sender, instance, created, **kwargs):
    # print(f'Sender: {sender}, Instance {instance}, Created {created}, {kwargs}')
    if created:
        instance.setup_task()