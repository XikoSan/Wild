# coding=utf-8
import datetime
import json
from decimal import Decimal
from django.apps import apps
from django.db import models
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule

from player.logs.gold_log import GoldLog
from player.logs.log import Log
from player.player import Player
from state.models.state import State
from storage.models.storage import Storage
from storage.views.storage.locks.get_storage import get_storage
from player.player_settings import PlayerSettings
from skill.models.excavation import Excavation
import redis


# запись об изучаемом навыке
class AutoMining(Log):
    # ресурс
    activityChoices = (
        ('gold', 'Золото'),
        ('oil', 'Нефть'),
        ('ore', 'Руда'),
    )
    resource = models.CharField(
        max_length=4,
        choices=activityChoices,
        blank=True,
        null=True,
        verbose_name='Ресурс'
    )

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
            name=self.player.nickname + ' собирает ' + self.get_resource_display(),
            task='crude_retrieve',
            # interval=schedule,
            crontab=schedule,
            args=json.dumps([self.pk]),
            start_time=timezone.now()
        )

        # если есть другое производство или работа - снимаем
        AutoProduce = apps.get_model('factory.AutoProduce')
        if AutoMining.objects.filter(player=self.player).exists():
            AutoMining.objects.filter(player=self.player).delete()

        if AutoProduce.objects.filter(player=self.player).exists():
            AutoProduce.objects.filter(player=self.player).delete()

        self.save()

    # получить указанный ресурсы
    @transaction.atomic
    def retrieve_crude(self):

        # удалять другие задачи на авто-производство и работу
        AutoProduce = apps.get_model('factory.AutoProduce')
        if AutoMining.objects.filter(player=self.player).exclude(pk=self.pk).exists():
            AutoMining.objects.filter(player=self.player).exclude(pk=self.pk).delete()

        if AutoProduce.objects.filter(player=self.player).exists():
            AutoProduce.objects.filter(player=self.player).delete()

        # прерывать, если дата создания + сутки > сейчас
        if self.dtime + datetime.timedelta(days=1) < timezone.now():
            self.delete()
            return

        player = Player.get_instance(pk=self.player.pk)

        # прерывать, если премиум-аккаунт истёк
        if player.premium < timezone.now():
            self.delete()
            return

        # если у игрока нет Склада в этом регионе, то Нефть и Руду собирать он не сможет
        if self.resource in ['ore', 'oil'] \
                and not Storage.actual.filter(owner=player, region=player.region).exists():
            self.delete()
            return

        if PlayerSettings.objects.filter(player=player, full_auto=True).exists():
            # если дайлик еще не заполнен
            if player.energy_consumption + player.paid_consumption < 3000:
                # время, когда можно перезаряжаться
                if player.last_refill <= timezone.now():
                    if player.bottles >= 100 - player.energy:
                        refill_value = 100 - player.energy

                        player.bottles -= refill_value
                        player.energy += refill_value
                        player.last_refill = timezone.now() + datetime.timedelta(seconds=599)

        if player.energy < 10:
            # ждем следующего цикла
            return

        # получаем ровные 10, 20...100 энергии
        count = int(player.energy // 10 * 10)

        if count == 0:
            # ждем следующего цикла
            return

        storage = None
        if self.resource in ['ore', 'oil']:
            storage = Storage.actual.get(owner=player, region=player.region)

        mined = False

        if self.resource == 'gold':
            # если запасов ресурса недостаточно
            if player.region.gold_has < Decimal((count / 10) * 0.01):
                # ждем следующего цикла
                return

            player.gold += count / 10
            mined = True

            GoldLog(player=player, gold=int(count / 10), activity_txt='aumine').save()

            player.region.gold_has -= Decimal((count / 10) * 0.01)

        elif self.resource == 'oil':
            # если запасов ресурса недостаточно
            if int(player.region.oil_has * 100) < count / 10:
                # ждем следующего цикла
                return

            # получаем запасы склада, с учетом блокировок
            goods = [player.region.oil_type]
            lock_storage = get_storage(storage, goods)
            # облагаем налогом добытую нефть
            total_oil = (count / 10) * 20
            taxed_oil = State.get_taxes(player.region, total_oil, 'oil', player.region.oil_type)

            # сохраняем информацию о том, сколько добыто за день
            r = redis.StrictRedis(host='redis', port=6379, db=0)
            # общее
            if r.exists("daily_" + player.region.oil_type):
                r.set("daily_" + player.region.oil_type, int(float(r.get("daily_" + player.region.oil_type))) + int(taxed_oil))

            else:
                r.set("daily_" + player.region.oil_type, int(taxed_oil))
            # регион
            if r.exists("daily_" + str(player.region.pk) + '_' + player.region.oil_type):
                r.set("daily_" + str(player.region.pk) + '_' + player.region.oil_type,
                      int(float(r.get("daily_" + str(player.region.pk) + '_' + player.region.oil_type))) + int(
                          taxed_oil))
            else:
                r.set("daily_" + str(player.region.pk) + '_' + player.region.oil_type, int(taxed_oil))

            # проверяем есть ли для него место на складе, с учетом блокировок
            if lock_storage.capacity_check(player.region.oil_type, taxed_oil):
                # начислить нефть
                mined = True
                setattr(storage, player.region.oil_type,
                        getattr(storage, player.region.oil_type) + taxed_oil)
            else:
                # если места нет или его меньше чем пак ресурсов, забиваем под крышку
                mined = True
                # устанавливаем новое значение как остаток до полного склада с учетом блокировок + старое значение ресурса
                setattr(storage, player.region.oil_type,
                        (getattr(storage, player.region.oil_type + '_cap') - getattr(lock_storage,
                                                                                     player.region.oil_type)) +
                        getattr(storage, player.region.oil_type)
                        )

            player.region.oil_has -= Decimal((count / 10) * 0.01)

        elif self.resource == 'ore':
            # если запасов ресурса недостаточноы
            if int(player.region.ore_has * 100) < count / 10:
                # ждем следующего цикла
                return

            goods = []
            for key in storage.minerals.keys():
                goods.append(key)
            lock_storage = get_storage(storage, goods)

            for mineral in storage.minerals.keys():
                # облагаем налогом добытую руду
                total_ore = (count / 50) * getattr(player.region, mineral + '_proc')
                # экскавация
                if Excavation.objects.filter(player=player, level__gt=0).exists():
                    total_ore = Excavation.objects.get(player=player).apply({'sum': total_ore})

                taxed_ore = State.get_taxes(player.region, total_ore, 'ore', mineral)

                # сохраняем информацию о том, сколько добыто за день
                r = redis.StrictRedis(host='redis', port=6379, db=0)
                if r.exists("daily_" + mineral):
                    r.set("daily_" + mineral,
                          int(float(r.get("daily_" + mineral))) + int(taxed_ore))
                else:
                    r.set("daily_" + mineral, int(taxed_ore))
                # регион
                if r.exists("daily_" + str(player.region.pk) + '_' + mineral):

                    r.set("daily_" + str(player.region.pk) + '_' + mineral,
                          int(float(r.get("daily_" + str(player.region.pk) + '_' + mineral))) + int(taxed_ore))
                else:
                    r.set("daily_" + str(player.region.pk) + '_' + mineral, int(taxed_ore))

                # проверяем есть ли место на складе
                if lock_storage.capacity_check(mineral, taxed_ore):
                    # начислить минерал
                    mined = True
                    setattr(storage, mineral,
                            getattr(storage, mineral) + taxed_ore)
                else:
                    # если места нет или его меньше чем пак ресурсов, забиваем под крышку
                    if taxed_ore > 0:
                        mined = True
                        # устанавливаем новое значение как остаток до полного склада с учетом блокировок + старое значение ресурса
                        setattr(storage, mineral,
                                getattr(storage, mineral + '_cap') - getattr(lock_storage, mineral) + getattr(storage,
                                                                                                              mineral))

            player.region.ore_has -= Decimal((count / 10) * 0.01)

        else:
            return

        if mined:
            if self.resource != 'gold':
                storage.save()
                player.energy_cons(count)

            else:
                player.energy -= count
                player.save()

            player.region.save()

    def __str__(self):
        return self.player.nickname + ' добывает ' + str(self.get_resource_display())

    # Свойства класса
    class Meta:
        verbose_name = "Автоматический сбор"
        verbose_name_plural = "Автоматически собираемые ресурсы"


# сигнал формирующий таску
@receiver(post_save, sender=AutoMining)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=AutoMining)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
