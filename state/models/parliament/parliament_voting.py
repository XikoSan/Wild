# coding=utf-8
import datetime
import json

from django.db import models
from django.db.models.signals import post_save
# from io import BytesIO
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from state.models.parliament.parliament import Parliament


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
    # переодическая таска
    task = models.OneToOneField(PeriodicTask, on_delete=models.DO_NOTHING, null=True, blank=True)

    # формируем переодическую таску
    def setup_task(self):

        if not PeriodicTask.objects.filter(
                name=f'{self.parliament.state.title}, id {self.parliament.pk} parl primaries').exists():

            # schedule, created = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.DAYS)
            schedule, created = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.MINUTES)

            self.task = PeriodicTask.objects.create(
                name=f'{self.parliament.state.title}, id {self.parliament.pk} parl primaries',
                task='finish_elections',
                interval=schedule,
                args=json.dumps([self.parliament.pk]),
                start_time=timezone.now(),
            )
            self.save()

    def delete_task(self):
        # проверяем есть ли таска
        if self.task is not None:
            task_identificator = self.task.id
            # убираем таску у экземпляра модели
            ParliamentVoting.objects.select_related('task').filter(pk=self.id).update(task=None)
            # удаляем таску
            PeriodicTask.objects.filter(pk=task_identificator).delete()

    def __str__(self):
        return self.parliament.state.title + "_" + self.voting_start.__str__()

    # Свойства класса
    class Meta:
        verbose_name = "Выборы"
        verbose_name_plural = "Выборы"


# сигнал прослушивающий создание праймериз, после этого формирующий таску
@receiver(post_save, sender=ParliamentVoting)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()
