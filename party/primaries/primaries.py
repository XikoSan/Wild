import json

import datetime

from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save

from django_celery_beat.models import ClockedSchedule, PeriodicTask

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
    prim_start = models.DateTimeField(default=timezone.now, blank=True, null=True)
    # время конца голосования
    prim_end = models.DateTimeField(default=None, blank=True, null=True)
    # переодическая таска
    task = models.OneToOneField(PeriodicTask, on_delete=models.DO_NOTHING, null=True, blank=True)

    # формируем переодическую таску
    def setup_task(self):

        if not PeriodicTask.objects.filter(name=f'{self.party.title}, id {self.party.pk} party primaries').exists():
            start_time = timezone.now() + datetime.timedelta(days=1)
            # start_time = timezone.now() + datetime.timedelta(minutes=1)
            clock, created = ClockedSchedule.objects.get_or_create(clocked_time=start_time)

            self.task = PeriodicTask.objects.create(
                name=f'{self.party.title}, id {self.party.pk} party primaries',
                task='finish_primaries',
                clocked=clock,
                one_off=True,
                args=json.dumps([self.party.pk]),
                start_time=timezone.now(),
            )
            self.save()

    # удаляем таску вместе с экземпляром модели
    def delete(self, *args, **kwargs):
        if self.task is not None:
            self.task.delete()

        return super(self.__class__, self).delete(*args, **kwargs)

    def __str__(self):
        if self.prim_end:
            return self.party.title + " ( " + self.prim_start.strftime("%m/%d/%Y") + ' - ' + self.prim_end.strftime(
                "%m/%d/%Y") + " )"
        else:
            return self.party.title + " ( " + self.prim_start.strftime("%m/%d/%Y") + " )"

    # Свойства класса
    class Meta:
        verbose_name = "Праймериз в партии"
        verbose_name_plural = "Праймериз"


# сигнал прослушивающий создание праймериз, после этого формирующий таску
@receiver(post_save, sender=Primaries)
def save_post(sender, instance, created, **kwargs):
    # print(f'Sender: {sender}, Instance {instance}, Created {created}, {kwargs}')
    if created:
        instance.setup_task()
