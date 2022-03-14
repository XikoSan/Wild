# coding=utf-8
import datetime
import json

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask

from player.player import Player
from state.models.state import State


class President(models.Model):
    # государство принадлежности
    state = models.OneToOneField(State, on_delete=models.CASCADE, verbose_name='Государство',
                                 related_name="pres_state")
    # игрок
    leader = models.ForeignKey(Player, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                               verbose_name='Президент', related_name="pres_leader")

    # переодическая таска
    task = models.OneToOneField(PeriodicTask, on_delete=models.DO_NOTHING, null=True, blank=True)

    # формируем переодическую таску
    def setup_task(self):
        start_time = timezone.now() + datetime.timedelta(days=1)
        # start_time = timezone.now() + datetime.timedelta(minutes=1)
        clock, created = ClockedSchedule.objects.get_or_create(clocked_time=start_time)

        self.task = PeriodicTask.objects.create(
            name=self.state.title + ', id преза ' + str(self.pk),
            task='start_presidential',
            clocked=clock,
            one_off=True,
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


# сигнал прослушивающий создание поста Президента
@receiver(post_save, sender=President)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()
