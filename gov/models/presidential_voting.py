# coding=utf-8
import datetime
import json

from django.db import models
from django.db.models.signals import post_save
# from io import BytesIO
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask, CrontabSchedule
from player.player import Player
from gov.models.president import President


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

        if not PeriodicTask.objects.filter(
                name=f'{self.president.state.title}, id {self.president.pk} pres elections').exists():

            foundation_day = timezone.now().weekday()

            if foundation_day == 6:
                cron_day = 1
            elif foundation_day == 5:
                cron_day = 0
            else:
                cron_day = foundation_day + 2

            schedule, created = CrontabSchedule.objects.get_or_create(
                minute=str(timezone.now().now().minute),
                hour=str(timezone.now().now().hour),
                day_of_week=cron_day,
                day_of_month='*',
                month_of_year='*',
            )

            self.task = PeriodicTask.objects.create(
                name=f'{self.president.state.title}, id {self.president.pk} pres elections',
                task='finish_presidential',
                crontab=schedule,
                one_off=False,
                args=json.dumps([self.president.pk]),
                start_time=timezone.now(),
            )
            self.save()

        else:
            # убираем таску у экземпляра модели, чтобы ее могли забрать последующие
            PresidentialVoting.objects.select_related('task').filter(president=president, task__isnull=False).update(
                task=None)

            self.task = PeriodicTask.objects.filter(name=f'{self.president.state.title}, id {self.president.pk} pres elections').first()
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
    if created:
        instance.setup_task()
