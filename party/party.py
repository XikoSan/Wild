import json
import sys
import datetime
from PIL import Image
from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.core.files.uploadedfile import InMemoryUploadedFile
from django_celery_beat.models import ClockedSchedule, PeriodicTask, CrontabSchedule

from region.models.region import Region

from io import BytesIO


# Create your models here.

class Party(models.Model):
    # название партии
    title = models.CharField(max_length=30, verbose_name='Название партии')
    # тип партии
    open = 'op'
    private = 'pt'
    partyTypeChoices = (
        (open, 'Открытая'),
        (private, 'Частная'),
    )
    type = models.CharField(
        max_length=2,
        choices=partyTypeChoices,
        default=open,
    )

    # время основания партии
    foundation_date = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True)
    # описание партии
    description = models.CharField(max_length=300, blank=True, null=True, verbose_name='Описание партии')
    # картинка партии
    image = models.ImageField(upload_to='img/party_avatars/', blank=True, null=True, verbose_name='Герб партии')
    # картинка партийного фона
    members_image = models.ImageField(upload_to='img/party_backs/', blank=True, null=True,
                                      verbose_name='Ссылка партийный фон')
    # регион партии
    region = models.ForeignKey(Region, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                               verbose_name='Регион размещения', related_name="party_region")

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    # # id фонового процесса (начала или конца праймериз)
    # task_id = models.CharField(max_length=150, blank=True, null=True, verbose_name='id фонового процесса')
    # переодическая таска
    task = models.OneToOneField(PeriodicTask, on_delete=models.DO_NOTHING, null=True, blank=True)

    # формируем переодическую таску
    def setup_task(self):
        # start_time = timezone.now() + datetime.timedelta(days=7)
        # clock, created = ClockedSchedule.objects.get_or_create(clocked_time=start_time)

        foundation_day = self.foundation_date.weekday()

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
            name='Начало праймериз, id ' + str(self.pk),
            task='start_primaries',
            crontab=schedule,
            # clocked=clock,
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
            Party.objects.select_related('task').filter(pk=self.id).update(task=None)
            # удаляем таску
            PeriodicTask.objects.filter(pk=task_identificator).delete()

    def __str__(self):
        return self.title

    # Свойства класса
    class Meta:
        verbose_name = "Партия"
        verbose_name_plural = "Партии"


# сигнал прослушивающий создание партии, после этого формирующий таску
@receiver(post_save, sender=Party)
def save_post(sender, instance, created, **kwargs):
    # print(f'Sender: {sender}, Instance {instance}, Created {created}, {kwargs}')
    if created:
        instance.setup_task()

# сигнал удаляющий таску
@receiver(post_delete, sender=Party)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
