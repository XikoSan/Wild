# coding=utf-8

import datetime
import json

from django.db import models
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask

from player.player import Player
from state.models.parliament.parliament import Parliament


# Абстрактный класс законопроекта
# Позволяет создавать законопроекты разных типов при общей механике создания их в парламенте
class Bill(models.Model):
    # признак того что законопроект рассматривается сейчас
    running = models.BooleanField(default=False, verbose_name='Рассматривается')
    # решение:
    accepted = 'ac'
    rejected = 'rj'
    canceled = 'cn'
    billEndChoices = (
        (accepted, 'Принят'),
        (rejected, 'Отклонён'),
        (canceled, 'Отменён'),
    )
    type = models.CharField(
        max_length=2,
        choices=billEndChoices,
        blank=True,
        null=True,
        default=None,
        verbose_name='Решение',
    )
    # стоимость законопроекта в ресурсах
    # Наличные
    cash_cost = models.BigIntegerField(default=0, verbose_name='Наличные')

    # парламент, которому принадлежит законопроект
    parliament = models.ForeignKey(Parliament, on_delete=models.CASCADE, verbose_name='Закон в парламенте')
    # инициатор - предложивший зп
    initiator = models.ForeignKey(Player, default=None, null=True, on_delete=models.SET_NULL, verbose_name='Инициатор')
    # время начала голосования
    voting_start = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True,
                                        verbose_name='Время начала рассмотрения')
    # время завершения рассмотрения зп (момент, когда он был принят или отклонен - или сутки с момента начала)
    voting_end = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True, null=True,
                                      verbose_name='Время завершения рассмотрения')

    # голоса "за"
    votes_pro = models.ManyToManyField(Player, blank=True,
                                       related_name='%(class)s_votes_pro',
                                       verbose_name='Голоса "за"')
    # голоса "против"
    votes_con = models.ManyToManyField(Player, blank=True,
                                       related_name='%(class)s_votes_con',
                                       verbose_name='Голоса "против"')

    # переодическая таска
    task = models.OneToOneField(PeriodicTask, on_delete=models.DO_NOTHING, null=True, blank=True)

    # возможность принять закон досрочно
    accept_ahead = True

    # процент голосов от всего парламента, который нужен для принятия досрочно
    ahead_percent = 51

    # процент голосов "за", который надо преодолеть, чтобы принять закон
    acceptation_percent = 50

    # Указание абстрактности класса
    class Meta:
        abstract = True

    @staticmethod
    def new_bill(request, player, parliament):
        return

    # выполнить законопроект
    def do_bill(self):
        return

    # получить шаблон черновика законопроекта
    @staticmethod
    def get_draft(state):
        return

    # получить шаблон законопроекта в парламенте
    def get_bill(self, player, minister, president):
        return

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):
        return

    # формируем переодическую таску
    def setup_task(self):
        start_time = timezone.now() + datetime.timedelta(days=1)
        # start_time = timezone.now() + datetime.timedelta(minutes=1)

        clock, created = ClockedSchedule.objects.get_or_create(clocked_time=start_time)

        self.task = PeriodicTask.objects.create(
            name=self.__class__.__name__ + ', id ' + str(self.pk),
            task='run_bill',
            clocked=clock,
            one_off=True,
            args=json.dumps([self.__class__.__name__, self.id]),
            start_time=timezone.now()
        )
        self.save()
