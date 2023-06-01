# coding=utf-8
import datetime
import json
import redis
from django.apps import apps
from decimal import Decimal
from django.db import models
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule
from django.apps import apps
from player.logs.gold_log import GoldLog
from player.logs.log import Log
from player.player import Player
from player.player_settings import PlayerSettings
from django.apps import apps
from factory.models.production_log import ProductionLog
from .project import Project
from storage.models.storage import Storage
from storage.views.storage.locks.get_storage import get_storage
from math import ceil

# автоматическое производство
class AutoProduce(Log):
    # склад производства
    storage = models.ForeignKey(Storage, default=None, on_delete=models.CASCADE,
                                     verbose_name='Склад', related_name="produce_storage")

    # товар для производства
    good = models.CharField(
        max_length=10,
        choices=Project.schemas,
        blank=True,
        null=True,
        verbose_name='Ресурс'
    )

    # номер схемы
    schema = models.CharField(max_length=1, verbose_name='Номер схемы')

    # переодическая таска
    task = models.OneToOneField(PeriodicTask, on_delete=models.DO_NOTHING, null=True, blank=True)

    # формируем переодическую таску
    def setup_task(self):

        min = None
        if len(str(timezone.now().minute)) == 1:
            min = str(timezone.now().minute)
        else:
            min = str(timezone.now().minute)[1]

        steps = min

        for dec in ['1', '2', '3', '4', '5']:
            steps += ', ' + dec + min

        if CrontabSchedule.objects.filter(
                minute=steps,
                hour='*',
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
        ).exists():

            schedule = CrontabSchedule.objects.filter(
                minute=steps,
                hour='*',
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
            ).first()

        else:

            schedule = CrontabSchedule.objects.create(
                minute=steps,
                hour='*',
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
            )

        # -----------

        # если есть другое производство или работа - снимаем
        AutoMining = apps.get_model('player.AutoMining')
        if AutoMining.objects.filter(player=self.player).exists():
            AutoMining.objects.filter(player=self.player).delete()

        if AutoProduce.objects.filter(player=self.player).exists():
            AutoProduce.objects.filter(player=self.player).delete()

        # -----------

        self.task = PeriodicTask.objects.create(
            name=self.player.nickname + ' производит ' + self.get_good_display(),
            task='good_produce',
            # interval=schedule,
            crontab=schedule,
            args=json.dumps([self.pk]),
            start_time=timezone.now()
        )

        self.save()

    # получить указанный ресурсы
    @transaction.atomic
    def produce_good(self):

        # удалять другие задачи на авто-производство и работу
        AutoMining = apps.get_model('player.AutoMining')
        if AutoMining.objects.filter(player=self.player).exists():
            AutoMining.objects.filter(player=self.player).delete()

        if AutoProduce.objects.filter(player=self.player).exclude(pk=self.pk).exists():
            AutoProduce.objects.filter(player=self.player).exclude(pk=self.pk).delete()

        # прерывать, если дата создания + сутки > сейчас
        if self.dtime + datetime.timedelta(days=1) < timezone.now():
            self.delete()
            return

        player = Player.get_instance(pk=self.player.pk)

        # прерывать, если премиум-аккаунт истёк
        if player.premium < timezone.now():
            self.delete()
            return

        if PlayerSettings.objects.filter(player=player, full_auto=True).exists():
            # если дейлик еще не заполнен
            if player.energy_consumption + player.paid_consumption < 3000:
                # время, когда можно перезаряжаться
                if player.last_refill <= timezone.now():
                    if player.bottles >= 100 - player.energy:
                        refill_value = 100 - player.energy

                        player.bottles -= refill_value
                        player.energy += refill_value
                        player.last_refill = timezone.now() + datetime.timedelta(seconds=599)

        # получаем схему производства
        try:
            schema = getattr(Project, self.good)['resources'][int(self.schema) - 1]

        except IndexError:
            # если схемы с таким номером нет - ошибка, уадаляемся
            self.delete()
            return

        # получаем число юнитов, которое может быть произведено по этой схеме
        price = getattr(Project, self.good)['energy']
        count = int(player.energy // price * price)

        consignment = 1

        # только для материалов
        if self.good in getattr(Storage, 'materials').keys():
            # если изучена Стандартизация
            Standardization = apps.get_model('skill.Standardization')
            if Standardization.objects.filter(player=player, level__gt=0).exists():
                # лимит производства на единицу энергии
                consignment = Standardization.objects.get(player=player).level + 1
                # новое количество товара, которое можно сделать за эту энергию
                count = player.energy // price * consignment

        # только для юнитов
        if self.good in getattr(Storage, 'units').keys():
            # если изучено Режимное производство
            MilitaryProduction = apps.get_model('skill.MilitaryProduction')
            if MilitaryProduction.objects.filter(player=player, level__gt=0).exists():
                # лимит производства на единицу энергии
                consignment = MilitaryProduction.objects.get(player=player).level + 1
                # новое количество товара, которое можно сделать за эту энергию
                count = player.energy // price * consignment

        if count == 0:
            # ждем следующего цикла
            return

        lock_storage = get_storage(self.storage, [self.good, ])

        min_count = count

        # для каждого сырья в схеме производства
        for material in schema.keys():
            # узнать, на сколько хватает запасов на выбранном складе
            if schema[material] * min_count > getattr(lock_storage, material):
                min_count = getattr(lock_storage, material) // schema[material]

        count = min_count

        # узнать, хватает ли места на складе для нового товара
        if count + getattr(lock_storage, self.good) > getattr(lock_storage, self.good + '_cap'):
            # запишем, сколько влезает
            count = getattr(lock_storage, self.good + '_cap') - getattr(lock_storage, self.good)

        if count == 0:
            # если ресы закончились - завершаемся
            self.delete()
            return

        player.energy_cons(ceil(count / consignment) * price, mul=2)

        # создаём лог производства
        ProductionLog.objects.create(player=player,
                                     prod_storage=lock_storage,
                                     good_move='incom',
                                     good=self.good,
                                     prod_value=count,
                                     )

        # для каждого сырья в схеме
        for material in schema.keys():
            # установить новое значени склада
            setattr(lock_storage, material, getattr(lock_storage, material) - (schema[material] * count))
            # залогировать траты со склада
            # создаём лог производства
            ProductionLog.objects.create(player=player,
                                         prod_storage=lock_storage,
                                         good_move='outcm',
                                         good=material,
                                         prod_value=schema[material] * count,
                                         )

        # добавить товар на склад
        setattr(lock_storage, self.good, getattr(lock_storage, self.good) + count)
        # сохранить склад
        lock_storage.save()

        # удаляем записи старше месяца
        ProductionLog.objects.filter(player=player, dtime__lt=timezone.now() - datetime.timedelta(days=30)).delete()

    def __str__(self):
        return self.player.nickname + ' производит ' + str(self.get_good_display())

    # Свойства класса
    class Meta:
        verbose_name = "Автоматическое производство"
        verbose_name_plural = "Автоматические производства"


# сигнал формирующий таску
@receiver(post_save, sender=AutoProduce)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=AutoProduce)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
