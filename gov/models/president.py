# coding=utf-8
import datetime
import json
import pytz
from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask, CrontabSchedule

from player.player import Player
from state.models.state import State

import state

class President(models.Model):
    # государство принадлежности
    state = models.OneToOneField(State, on_delete=models.CASCADE, verbose_name='Государство',
                                 related_name="pres_state")
    # игрок
    leader = models.ForeignKey(Player, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                               verbose_name='Президент', related_name="pres_leader")

    # время создания должности
    # может отличаться от государственного, если, к примеру, вводили диктатуру
    foundation_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    # день выборов
    elections_day = models.IntegerField(default=0, verbose_name='День выборов')

    # переодическая таска
    task = models.OneToOneField(PeriodicTask, on_delete=models.DO_NOTHING, null=True, blank=True)

    # формируем переодическую таску
    def setup_task(self):

        from player.logs.print_log import log
        log(timezone.localtime(self.foundation_date, pytz.timezone('Europe/Moscow')))

        foundation_day = timezone.localtime(self.foundation_date, pytz.timezone('Europe/Moscow')).weekday()

        if foundation_day == 6:
            cron_day = 0
        else:
            cron_day = foundation_day + 1


        if CrontabSchedule.objects.filter(
                                            minute=str(timezone.localtime(self.foundation_date, pytz.timezone('Europe/Moscow')).minute),
                                            hour=str(timezone.localtime(self.foundation_date, pytz.timezone('Europe/Moscow')).hour),
                                            day_of_week=cron_day,
                                            day_of_month='*',
                                            month_of_year='*',
                                        ).exists():

            schedule = CrontabSchedule.objects.filter(
                                                        minute=str(timezone.localtime(self.foundation_date, pytz.timezone('Europe/Moscow')).minute),
                                                        hour=str(timezone.localtime(self.foundation_date, pytz.timezone('Europe/Moscow')).hour),
                                                        day_of_week=cron_day,
                                                        day_of_month='*',
                                                        month_of_year='*',
                                                       ).first()

        else:

            schedule = CrontabSchedule.objects.create(
                                                        minute=str(timezone.localtime(self.foundation_date, pytz.timezone('Europe/Moscow')).minute),
                                                        hour=str(timezone.localtime(self.foundation_date, pytz.timezone('Europe/Moscow')).hour),
                                                        day_of_week=cron_day,
                                                        day_of_month='*',
                                                        month_of_year='*',
                                                       )

        self.task = PeriodicTask.objects.create(
            name='Начало выборов, id преза ' + str(self.pk),
            task='start_presidential',
            crontab=schedule,
            args=json.dumps([self.id]),
            start_time=timezone.now()
        )
        self.save()

    def __str__(self):
        return self.state.title

    # Свойства класса
    class Meta:
        verbose_name = "Президент"
        verbose_name_plural = "Президенты"


# сигнал прослушивающий создание партии, после этого формирующий таску
@receiver(pre_save, sender=President)
def save_pre(sender, instance, raw, using, update_fields, **kwargs):
    instance.elections_day = timezone.localtime(instance.foundation_date, pytz.timezone('Europe/Moscow')).weekday()

# сигнал прослушивающий создание поста Президента
@receiver(post_save, sender=President)
def save_post(sender, instance, created, **kwargs):
    if created:
        eval(f"state.tasks.start_presidential({instance.id})")

    #     instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=President)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
