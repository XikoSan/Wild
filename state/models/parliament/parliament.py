# coding=utf-8
import datetime
import json

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
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

        schedule, created = CrontabSchedule.objects.get_or_create(
                                                                    minute=str(timezone.now().now().minute),
                                                                    hour=str(timezone.now().now().hour),
                                                                    day_of_week=cron_day,
                                                                    day_of_month='*',
                                                                    month_of_year='*',
                                                                   )

        self.task = PeriodicTask.objects.create(
            name=self.state.title + ', id парла ' + str(self.pk),
            task='start_elections',
            crontab=schedule,
            # one_off=True,
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
