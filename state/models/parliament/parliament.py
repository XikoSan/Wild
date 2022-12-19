# coding=utf-8
import datetime
import json

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask, CrontabSchedule

from state.models.state import State


class Parliament(models.Model):
    # размер парламента, мест
    size = models.IntegerField(default=10, validators=[MinValueValidator(10)])
    # государство принадлежности
    state = models.OneToOneField(State, on_delete=models.CASCADE, verbose_name='Государство', related_name="state")

    # переодическая таска
    task = models.OneToOneField(PeriodicTask, on_delete=models.DO_NOTHING, null=True, blank=True)

    # формируем переодическую таску
    def setup_task(self):

        foundation_day = self.state.foundation_date.weekday()

        if foundation_day == 6:
            cron_day = 0
        else:
            cron_day = foundation_day + 1

        if CrontabSchedule.objects.filter(
                                                    minute=str(timezone.now().now().minute),
                                                    hour=str(timezone.now().now().hour),
                                                    day_of_week=cron_day,
                                                    day_of_month='*',
                                                    month_of_year='*',
                                               ).exists():

            schedule = CrontabSchedule.objects.filter(
                                                        minute=str(timezone.now().now().minute),
                                                        hour=str(timezone.now().now().hour),
                                                        day_of_week=cron_day,
                                                        day_of_month='*',
                                                        month_of_year='*',
                                                    ).first()

        else:

            schedule = CrontabSchedule.objects.create(
                                                        minute=str(timezone.now().now().minute),
                                                        hour=str(timezone.now().now().hour),
                                                        day_of_week=cron_day,
                                                        day_of_month='*',
                                                        month_of_year='*',
                                                       )

        self.task = PeriodicTask.objects.create(
            name='Начало выборов, id парла ' + str(self.pk),
            task='start_elections',
            crontab=schedule,
            one_off=False,
            args=json.dumps([self.id]),
            start_time=timezone.now()
        )
        self.save()

    def delete_task(self):
        # проверяем есть ли таска
        if self.task is not None:
            task_identificator = self.task.id
            # убираем таску у экземпляра модели
            Parliament.objects.select_related('task').filter(pk=self.id).update(task=None)
            # удаляем таску
            PeriodicTask.objects.filter(pk=task_identificator).delete()

    def __str__(self):
        return self.state.title

    # Свойства класса
    class Meta:
        verbose_name = "Парламент"
        verbose_name_plural = "Парламенты"


# сигнал прослушивающий создание партии, после этого формирующий таску
@receiver(post_save, sender=Parliament)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=Parliament)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()