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

from storage.models.good import Good
from factory.models.blueprint import Blueprint
from factory.models.component import Component
from storage.views.storage.locks.get_storage import get_stocks
from storage.models.stock import Stock


# автоматическое производство
class AutoProduce(Log):
    # склад производства
    storage = models.ForeignKey(Storage, default=None, on_delete=models.CASCADE,
                                     verbose_name='Склад', related_name="produce_storage")

    # товар для производства
    old_good = models.CharField(
        max_length=10,
        choices=Project.schemas,
        blank=True, null=True, default=None,
        verbose_name='не используется'
    )

    # товар для производства
    good = models.ForeignKey(Good,
                             blank=True, null=True, default=None,
                             on_delete=models.CASCADE, verbose_name='Продукция')

    # номер схемы
    schema = models.IntegerField(default=1, verbose_name='Номер схемы')

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

        self.task = PeriodicTask.objects.create(
            name=self.player.nickname + ' производит ' + self.good.name,
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

        #   -----------------  

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
        if not Blueprint.objects.filter(pk=self.schema, good=self.good).exists():
            # если схемы с таким номером нет - ошибка, уадаляемся
            self.delete()
            return

        schema = Blueprint.objects.get(pk=self.schema)

        # получаем число юнитов, которое может быть произведено по этой схеме
        price = schema.energy_cost
        # лимит производства на единицу энергии
        consignment = ( player.knowledge // 25 ) + 1

        count = int(player.energy // price) * consignment

        # только для материалов
        if self.good.type == 'materials':
            # если изучена Стандартизация
            Standardization = apps.get_model('skill.Standardization')
            if Standardization.objects.filter(player=player, level__gt=0).exists():
                # лимит производства на единицу энергии
                consignment += Standardization.objects.get(player=player).level
                # новое количество товара, которое можно сделать за эту энергию
                count = player.energy // price * consignment

        # только для юнитов
        if self.good.type == 'units':
            # если изучено Режимное производство
            MilitaryProduction = apps.get_model('skill.MilitaryProduction')
            if MilitaryProduction.objects.filter(player=player, level__gt=0).exists():
                # лимит производства на единицу энергии
                consignment += MilitaryProduction.objects.get(player=player).level
                # новое количество товара, которое можно сделать за эту энергию
                count = player.energy // price * consignment

        if count == 0:
            # ждем следующего цикла
            return

        good = self.good
        goods = [self.good.name_ru, ]
        ret_stocks, ret_st_stocks = get_stocks(self.storage, goods)

        # список с сырьём и продукцией
        goods = [good,]

        components = Component.objects.filter(blueprint=schema)

        for component in components:
            # добавляем сырье в список товаров, которые обрабатываются
            goods.append(component.good)

        # получаем запасы для данного склада
        stocks = Stock.objects.select_for_update().filter(storage=self.storage, good__in=goods, stock__gt=0)

        min_count = count

        # узнаем на сколько хватит денег на складе
        if schema.cash_cost * min_count > self.storage.cash:
            min_count = self.storage.cash // schema.cash_cost

        # для каждого сырья в схеме производства
        for component in components:
            # таких запасов нет, зануляем
            if not stocks.filter(good=component.good).exists():
                min_count = 0
            # узнать, на сколько хватает запасов на выбранном складе
            elif component.count * min_count > stocks.get(good=component.good).stock:
                min_count = stocks.get(good=component.good).stock // component.count

        if min_count < count:
            count = min_count

        # узнать, хватает ли места на складе для нового товара
        sizetype_stocks = ret_st_stocks[good.size]
        if not self.storage.capacity_check(good.size, count, sizetype_stocks):
            # запишем, сколько влезает
            count = getattr(self.storage, good.size + '_cap') - sizetype_stocks

        if count <= 0:
            # если ресы закончились - завершаемся
            self.delete()
            return

        # player.energy_cons(value=ceil(count / consignment) * price, region=self.storage.region)
        player.energy_cons(value=ceil(count / consignment) * price, mul=1, region=self.storage.region)

        # создаём лог производства
        ProductionLog.objects.create(player=player,
                                     prod_storage=self.storage,
                                     good_move='incom',
                                     good=self.good,
                                     prod_value=count,
                                     )

        # списываем деньги отдельно
        self.storage.cash -= schema.cash_cost * count

        # для каждого сырья в схеме
        for component in components:
            # установить новое значение Запаса
            stock = stocks.get(good=component.good)
            stock.stock -= component.count * count
            stock.save()

            # залогировать траты со склада
            # создаём лог производства
            ProductionLog.objects.create(player=player,
                                         prod_storage=self.storage,
                                         good_move='outcm',
                                         good=component.good,
                                         prod_value=component.count * count,
                                         )

        # добавить товар на склад
        stock, created = Stock.objects.get_or_create(
            storage=self.storage,
            good=good,
        )
        stock.stock += count
        stock.save()
        # сохранить склад
        self.storage.save()

        # удаляем записи старше месяца
        ProductionLog.objects.filter(player=player, dtime__lt=timezone.now() - datetime.timedelta(days=30)).delete()

        r = redis.StrictRedis(host='redis', port=6379, db=0)
        if player.party:
            # партийная информация
            if r.exists("party_factory_" + str(player.party.pk)):
                r.set("party_factory_" + str(player.party.pk),
                      int(float(r.get("party_factory_" + str(player.party.pk)))) + count)
            else:
                r.set("party_factory_" + str(player.party.pk), count)

        if r.exists("all_factory"):
            r.set("all_factory", int(float(r.get("all_factory"))) + count)
        else:
            r.set("all_factory", count)


    def __str__(self):
        return self.player.nickname + ' производит ' + str(self.good.name)

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
