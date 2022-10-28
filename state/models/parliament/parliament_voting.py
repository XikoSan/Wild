# coding=utf-8
import datetime
import json

from django.db import models
from django.db.models.signals import post_save
# from io import BytesIO
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask, CrontabSchedule

from state.models.parliament.parliament import Parliament

# класс выборы
# parliament - парламент, в который проходят выборы
# время начала и конца выборов
class ParliamentVoting(models.Model):
    # признак того что выборы активны
    running = models.BooleanField(default=True, verbose_name='Идут сейчас')
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

            foundation_day = self.parliament.state.foundation_date.weekday()

            # день недели для окончания - на один больше
            if foundation_day == 6:
                cron_day = 1
            elif foundation_day == 5:
                cron_day = 0
            else:
                cron_day = foundation_day + 1

            schedule, created = CrontabSchedule.objects.get_or_create(
                minute=str(timezone.now().now().minute),
                hour=str(timezone.now().now().hour),
                day_of_week=cron_day,
                day_of_month='*',
                month_of_year='*',
            )

            self.task = PeriodicTask.objects.create(
                name=f'{self.parliament.state.title}, id {self.parliament.pk} parl primaries',
                task='finish_elections',
                # clocked=clock,
                one_off=False,
                crontab=schedule,
                args=json.dumps([self.parliament.pk]),
                start_time=timezone.now(),
            )
            self.save()

        else:
            # убираем таску у экземпляра модели, чтобы ее могли забрать последующие
            ParliamentVoting.objects.select_related('task').filter(parliament=self.parliament, task__isnull=False).update(
                task=None)

            self.task = PeriodicTask.objects.filter(name=f'{self.parliament.state.title}, id {self.parliament.pk} parl primaries').first()
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
