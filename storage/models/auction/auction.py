# coding=utf-8
import datetime
import json
from django.apps import apps
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask

from player.actual_manager import ActualManager
from state.models.treasury_lock import TreasuryLock
from storage.models.storage import Storage


# Аукцион покупки
# todo: когда будешь делать аукцион продажи, пропиши его в войнах
class BuyAuction(models.Model):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей

    # блокировка казны
    treasury_lock = models.ForeignKey(TreasuryLock, default=None, on_delete=models.CASCADE,
                                      verbose_name='Блокировка', related_name="treasury_lock")

    # продаваемый товар
    good = models.CharField(
        max_length=10,
        choices=Storage.get_choises(),
        default='coal',
        verbose_name='Товар',
    )

    # время создания предложения
    create_date = models.DateTimeField(default=None, null=True, blank=True)
    # время закрытия предложения
    accept_date = models.DateTimeField(default=None, null=True, blank=True)

    # переодическая таска
    task = models.OneToOneField(PeriodicTask, on_delete=models.DO_NOTHING, null=True, blank=True)

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    # выполнить аукцион
    def run(self):
        # получаем все лоты аукциона
        lot_class = None
        for model in apps.get_models():
            if model.__name__ == 'AuctionLot':
                lot_class = model
                break

        lots = lot_class.actual.filter(auction=self)

        # для каждого лота:
        for lot in lots:

            # выполнить лот
            price = lot.run()
            # если вернулась цена на списание:
            if price:
                # начисляем в казну объем лота
                setattr(self.treasury_lock.lock_treasury, self.good,
                        getattr(self.treasury_lock.lock_treasury, self.good) + lot.count)
                # списываем из блокировки казны сумму = цена ставки * объем лота
                self.treasury_lock.lock_count -= price * lot.count

        if self.treasury_lock.lock_count > 0:
            # возвращаем оставшиеся в блокировке деньги в казну
            setattr(self.treasury_lock.lock_treasury, self.treasury_lock.lock_good,
                    getattr(self.treasury_lock.lock_treasury,
                            self.treasury_lock.lock_good) + self.treasury_lock.lock_count)
        # сохранить казну
        self.treasury_lock.lock_treasury.save()

        # удаляем блокировку казны (отметка)
        self.treasury_lock.deleted = True
        # сохраяем блокировку
        self.treasury_lock.save()

        # ставим время завершения аукциона
        self.accept_date = timezone.now()
        # сохраняем аукцион
        self.save()

    # формируем переодическую таску
    def setup_task(self):
        start_time = timezone.now() + datetime.timedelta(days=1)
        # start_time = timezone.now() + datetime.timedelta(minutes=1)

        clock, created = ClockedSchedule.objects.get_or_create(clocked_time=start_time)

        self.task = PeriodicTask.objects.create(
            name=self.__class__.__name__ + ', id ' + str(self.pk),
            task='run_auction',
            clocked=clock,
            one_off=True,
            args=json.dumps([self.id]),
            start_time=timezone.now()
        )
        self.save()


    def delete_task(self):
        # проверяем есть ли таска
        if self.task is not None:
            task_identificator = self.task.id
            # убираем таску у экземпляра модели
            BuyAuction.objects.select_related('task').filter(pk=self.pk).update(task=None, deleted=True)
            # удаляем таску
            PeriodicTask.objects.filter(pk=task_identificator).delete()

    def __str__(self):
        return "Закупочный аукцион"

    # Свойства класса
    class Meta:
        verbose_name = "Закупочный аукцион"
        verbose_name_plural = "Закупочные аукционы"


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=BuyAuction)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=BuyAuction)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()