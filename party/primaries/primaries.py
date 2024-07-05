import datetime
import json
import pytz
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask, CrontabSchedule

from party.party import Party


# класс праймериз
# parliament - парламент, в который проходят выборы
# время начала и конца выборов
class Primaries(models.Model):
    # признак того что праймериз активны
    running = models.BooleanField(default=True, verbose_name='Идут прямо сейчас')
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
        foundation_day = timezone.localtime(self.party.foundation_date, pytz.timezone('Europe/Moscow')).weekday()
        # день недели для окончания - на один больше
        if foundation_day == 6:
            cron_day = 1
        elif foundation_day == 5:
            cron_day = 0
        else:
            cron_day = foundation_day + 2

        if CrontabSchedule.objects.filter(
                minute=str(timezone.localtime(self.party.foundation_date, pytz.timezone('Europe/Moscow')).minute),
                hour=str(timezone.localtime(self.party.foundation_date, pytz.timezone('Europe/Moscow')).hour),
                day_of_week=cron_day,
                day_of_month='*',
                month_of_year='*',
        ).exists():

            schedule = CrontabSchedule.objects.filter(
                minute=str(timezone.localtime(self.party.foundation_date, pytz.timezone('Europe/Moscow')).minute),
                hour=str(timezone.localtime(self.party.foundation_date, pytz.timezone('Europe/Moscow')).hour),
                day_of_week=cron_day,
                day_of_month='*',
                month_of_year='*',
            ).first()

        else:

            schedule = CrontabSchedule.objects.create(
                minute=str(timezone.localtime(self.party.foundation_date, pytz.timezone('Europe/Moscow')).minute),
                hour=str(timezone.localtime(self.party.foundation_date, pytz.timezone('Europe/Moscow')).hour),
                day_of_week=cron_day,
                day_of_month='*',
                month_of_year='*',
            )

        Primaries.objects.filter(party=self.party, task__isnull=False).update(task=None)
        PeriodicTask.objects.filter(name='Конец праймериз, id ' + str(self.party.pk)).delete()

        self.task = PeriodicTask.objects.create(
            enabled = True,
            name='Конец праймериз, id ' + str(self.party.pk),
            task='finish_primaries',
            crontab=schedule,
            # clocked=clock,
            one_off=True,
            args=json.dumps([self.party.pk]),
            start_time=timezone.now(),
        )
        self.save()

    def delete_task(self):
        # проверяем есть ли таска
        if self.task is not None:
            task_identificator = self.task.id
            # убираем таску у экземпляра модели
            Primaries.objects.select_related('task').filter(pk=self.id).update(task=None)
            # удаляем таску
            PeriodicTask.objects.filter(pk=task_identificator).delete()

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
    pass
    # if created:
    #     instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=Primaries)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
