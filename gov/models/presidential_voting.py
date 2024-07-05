# coding=utf-8
import datetime
import json
import pytz
from django.db import models
from django.db.models.signals import post_save, post_delete
# from io import BytesIO
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask, CrontabSchedule

from gov.models.president import President
from player.player import Player


# класс выборы президента
# president - должность, на которую проходят выборы
# время начала и конца выборов
class PresidentialVoting(models.Model):
    # признак того что выборы активны
    running = models.BooleanField(default=True, verbose_name='Идут сейчас')
    # парламент, в который происходят выборы
    president = models.ForeignKey(President, on_delete=models.CASCADE, verbose_name='Должность')

    # список кандидатов
    candidates = models.ManyToManyField(Player, blank=True,
                                        related_name='%(class)s_candidates',
                                        verbose_name='Кандидаты')

    # время начала голосования
    voting_start = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True)
    # время конца голосования
    voting_end = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True)

    # переодическая таска
    task = models.OneToOneField(PeriodicTask, on_delete=models.DO_NOTHING, null=True, blank=True)

    # формируем переодическую таску
    def setup_task(self):

        foundation_day = timezone.localtime(self.president.foundation_date, pytz.timezone('Europe/Moscow')).weekday()


        if foundation_day == 6:
            cron_day = 1
        elif foundation_day == 5:
            cron_day = 0
        else:
            cron_day = foundation_day + 2

        if CrontabSchedule.objects.filter(
                minute=str(timezone.localtime(self.president.foundation_date, pytz.timezone('Europe/Moscow')).minute),
                hour=str(timezone.localtime(self.president.foundation_date, pytz.timezone('Europe/Moscow')).hour),
                day_of_week=cron_day,
                day_of_month='*',
                month_of_year='*',
        ).exists():

            schedule = CrontabSchedule.objects.filter(
                minute=str(timezone.localtime(self.president.foundation_date, pytz.timezone('Europe/Moscow')).minute),
                hour=str(timezone.localtime(self.president.foundation_date, pytz.timezone('Europe/Moscow')).hour),
                day_of_week=cron_day,
                day_of_month='*',
                month_of_year='*',
            ).first()

        else:

            schedule = CrontabSchedule.objects.create(
                minute=str(timezone.localtime(self.president.foundation_date, pytz.timezone('Europe/Moscow')).minute),
                hour=str(timezone.localtime(self.president.foundation_date, pytz.timezone('Europe/Moscow')).hour),
                day_of_week=cron_day,
                day_of_month='*',
                month_of_year='*',
            )

        PresidentialVoting.objects.filter(president=self.president, task__isnull=False).update(task=None)
        PeriodicTask.objects.filter(name='Конец выборов, id преза ' + str(self.president.pk)).delete()

        self.task = PeriodicTask.objects.create(
            enabled = True,
            name='Конец выборов, id преза ' + str(self.president.pk),
            task='finish_presidential',
            crontab=schedule,
            one_off=False,
            args=json.dumps([self.president.pk]),
            start_time=timezone.now(),
        )
        self.save()

    def delete_task(self):
        # проверяем есть ли таска
        if self.task is not None:
            task_identificator = self.task.id
            # убираем таску у экземпляра модели
            PresidentialVoting.objects.select_related('task').filter(pk=self.id).update(task=None)
            # удаляем таску
            PeriodicTask.objects.filter(pk=task_identificator).delete()

    def __str__(self):
        return self.president.state.title + "_" + self.voting_start.__str__()

    # Свойства класса
    class Meta:
        verbose_name = "Выборы президента"
        verbose_name_plural = "Выборы президента"


# сигнал прослушивающий создание праймериз, после этого формирующий таску
@receiver(post_save, sender=PresidentialVoting)
def save_post(sender, instance, created, **kwargs):
    pass
    # if created:
    #     instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=PresidentialVoting)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
