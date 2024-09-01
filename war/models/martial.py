# coding=utf-8
import datetime
import json
import math
import pytz
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask, CrontabSchedule

from region.models.region import Region
from state.models.state import State

class Martial(models.Model):
    # признак того что военное положение активно
    active = models.BooleanField(default=False, verbose_name='Активно')

    # регион
    region = models.ForeignKey(Region, blank=False, on_delete=models.CASCADE,
                               verbose_name='Регион', related_name="reg_mart")

    state = models.ForeignKey(State, blank=False, on_delete=models.CASCADE,
                              verbose_name='Государство', related_name="mar_state")

    # дней с объявления прошло
    days_left = models.IntegerField(default=0, verbose_name='Прошло дней')

    # время завершения работы ВП
    active_end = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True, null=True,
                                      verbose_name='Время завершения ВП')

    # переодическая таска
    task = models.OneToOneField(PeriodicTask, on_delete=models.DO_NOTHING, null=True, blank=True)

    # отключение военки
    def disable_martial(self):
        task = self.task

        self.task = None
        self.active_end = timezone.now()
        self.active = False
        self.save()

        task.delete()

    # формируем переодическую таску
    def setup_task(self):

        now_time = timezone.now()

        schedule = CrontabSchedule.objects.create(
            minute='*',
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )

        # if CrontabSchedule.objects.filter(
        #         minute=str(timezone.localtime(now_time, pytz.timezone('Europe/Moscow')).minute),
        #         hour=str(timezone.localtime(now_time, pytz.timezone('Europe/Moscow')).hour),
        #         day_of_week='*',
        #         day_of_month='*',
        #         month_of_year='*',
        # ).exists():
        #
        #     schedule = CrontabSchedule.objects.filter(
        #         minute=str(timezone.localtime(now_time, pytz.timezone('Europe/Moscow')).minute),
        #         hour=str(timezone.localtime(now_time, pytz.timezone('Europe/Moscow')).hour),
        #         day_of_week='*',
        #         day_of_month='*',
        #         month_of_year='*',
        #     ).first()
        #
        # else:
        #
        #     schedule = CrontabSchedule.objects.create(
        #         minute=str(timezone.localtime(now_time, pytz.timezone('Europe/Moscow')).minute),
        #         hour=str(timezone.localtime(now_time, pytz.timezone('Europe/Moscow')).hour),
        #         day_of_week='*',
        #         day_of_month='*',
        #         month_of_year='*',
        #     )

        self.task = PeriodicTask.objects.create(
            enabled=True,
            name='Военное положение, id ' + str(self.pk),
            task='pay_martial',
            crontab=schedule,
            args=json.dumps([self.id]),
            start_time=timezone.now()
        )
        self.save()

    def __str__(self):
        return self.region.region_name

    # Свойства класса
    class Meta:
        verbose_name = "Активное военное положение"
        verbose_name_plural = "Активные военные положения"


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=Martial)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=Martial)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
