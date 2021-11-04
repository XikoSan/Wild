import json

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from party.party import Party


# класс праймериз
# parliament - парламент, в который проходят выборы
# время начала и конца выборов
class Primaries(models.Model):
    # признак того что праймериз активны
    running = models.BooleanField(default=False, verbose_name='Идут прямо сейчас')
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

        if not PeriodicTask.objects.filter(name=f'{self.party.title}, id {self.party.pk} party primaries').exists():
            schedule, created = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.DAYS)
            # schedule, created = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.MINUTES)

            self.task = PeriodicTask.objects.create(
                name=f'{self.party.title}, id {self.party.pk} party primaries',
                task='finish_primaries',
                interval=schedule,
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
    if created:
        instance.setup_task()
