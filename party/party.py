import json

import datetime

from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save

from django_celery_beat.models import IntervalSchedule, PeriodicTask

from region.region import Region

# from PIL import Image
# from io import BytesIO
# from django.core.files.uploadedfile import InMemoryUploadedFile
# import sys
# import gamecore.all_models.region as rgn



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
    task = models.OneToOneField(PeriodicTask, on_delete = models.DO_NOTHING, null = True, blank = True)

    # формируем переодическую таску
    def setup_task(self):
        # schedule, created = IntervalSchedule.objects.get_or_create(every = 7, period=IntervalSchedule.DAYS)IntervalSchedule.SECONDS
        schedule, created = IntervalSchedule.objects.get_or_create(every = 2, period=IntervalSchedule.MINUTES)
        self.task = PeriodicTask.objects.create(
            name = self.title,
            task = 'start_primaries',
            interval = schedule,
            args = json.dumps([self.id]),
            start_time = timezone.now()
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
