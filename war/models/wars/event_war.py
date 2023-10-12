# coding=utf-8
import datetime
import os
import plotly.graph_objects as go
import pytz
import redis
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.shortcuts import redirect, render
from django.utils import timezone
from django_celery_beat.models import PeriodicTask

from player.player import Player
from player.views.timers import interval_in_seconds, format_time
from skill.models.scouting import Scouting
from storage.models.stock import Stock
from storage.models.storage import Storage
from war.models.wars.player_damage import PlayerDamage
from war.models.wars.unit import Unit
from war.models.wars.war import War
from war.models.wars.war_side import WarSide


# класс ивентовой войны
class EventWar(War):
    # прочность Штаба
    hq_points = models.BigIntegerField(default=0, verbose_name='Прочность Штаба')

    # стороны войны
    war_side = GenericRelation(WarSide)
    # урон в этой войне
    war_damage = GenericRelation(PlayerDamage)

    def __str__(self):
        return 'Тестовая война в регионе ' + getattr(self.agr_region, 'region_name')

    # Свойства класса
    class Meta:
        verbose_name = "Тестовая война"
        verbose_name_plural = "Тестовые войны"

    # просчитать раунд войны
    def war_round(self):
        self.round += 1
        r = redis.StrictRedis(host='redis', port=6379, db=0)

        agr_damage = r.hget(f'{self.__class__.__name__}_{self.pk}_dmg', 'agr')
        if not agr_damage:
            agr_damage = 0
        else:
            agr_damage = int(agr_damage)

        def_damage = r.hget(f'{self.__class__.__name__}_{self.pk}_dmg', 'def')
        if not def_damage:
            def_damage = 0
        else:
            def_damage = int(def_damage)

        self.hq_points = def_damage - agr_damage

        # сохраняем очки урона в график
        graph = []
        timestamp = str(datetime.datetime.now().timestamp()).split('.')[0]

        if self.graph:
            graph = eval(self.graph)

            if not graph[-1][1] ==  self.hq_points:
                graph.append((timestamp, self.hq_points))
        else:
            graph.append((timestamp, self.hq_points))

        self.graph = str(graph)

        # если последний раунд - на выход
        if self.round == 1440:
            self.war_end()

        self.save()

    # завершить войну
    def war_end(self):
        pk = self.task.pk
        self.task = None
        self.running = False
        self.end_time = timezone.now()
        self.save()
        PeriodicTask.objects.filter(pk=pk).delete()

    def get_page(self, request):
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        premium = False

        if player.premium > timezone.now():
            premium = True

        # agr_side = self.war_side.get(side='agr', object_id=self.pk)
        # def_side = self.war_side.get(side='def', object_id=self.pk)

        r = redis.StrictRedis(host='redis', port=6379, db=0)

        agr_damage = r.hget(f'{self.__class__.__name__}_{self.pk}_dmg', 'agr')
        if not agr_damage:
            agr_damage = 0
        else:
            agr_damage = int(agr_damage)

        def_damage = r.hget(f'{self.__class__.__name__}_{self.pk}_dmg', 'def')
        if not def_damage:
            def_damage = 0
        else:
            def_damage = int(def_damage)

        war_countdown = interval_in_seconds(
            object=self,
            start_fname='start_time',
            end_fname=None,
            delay_in_sec=86400
        )

        dtime_str = format_time(war_countdown)

        agr_char_list = self.war_damage.filter(object_id=self.pk, side='agr')
        def_char_list = self.war_damage.filter(object_id=self.pk, side='def')

        in_region = False
        storages = []

        units = Unit.objects.all()
        # фактические запасы оружия на доступном складе
        units_dict = {}

        unit_goods = []
        for unit in units:
            unit_goods.append(unit.good)

        if player.region == self.agr_region or player.region == self.def_region:
            in_region = True
            if Storage.actual.filter(owner=player, region=player.region).exists():

                storage = Storage.actual.get(owner=player, region=player.region)
                storages.append(storage)

                weapons = Stock.objects.filter(storage=storage, good__in=unit_goods, stock__gt=0)

                for weapon in weapons:
                    units_dict[weapon.good] = weapon.stock

        # --------------------------------------------------------------------------------------------
        data = []
        graph_html = None
        if self.graph:
            data = eval(self.graph)

        if data:
            # Разделите список на два отдельных списка: timestamps и scores
            timestamps, scores = zip(*data)

            # Преобразуйте значения timestamps в объекты datetime
            timestamps = [datetime.datetime.fromtimestamp(int(timestamp)).astimezone(tz=pytz.timezone(player.time_zone)) for timestamp in timestamps]

            # Создайте объект Scatter для построения графика
            fig = go.Figure(data=go.Scatter(x=timestamps, y=scores, mode='lines+markers'))

            # Настройте макет графика
            fig.update_layout(
                title='Score Changes Over Time',
                xaxis_title='Timestamp',
                yaxis_title='Score'
            )

            # Преобразуйте график в HTML и сохраните его в переменную
            graph_html = fig.to_html(full_html=False)
        # --------------------------------------------------------------------------------------------

        http_use = False
        if os.getenv('HTTP_USE'):
            http_use = True

        # отправляем в форму
        return render(request, 'war/redesign/' + self.__class__.__name__ + '.html', {
            # самого игрока
            'player': player,
            'premium': premium,
            # в зоне боевых действий
            'in_region': in_region,
            # склад
            'storages': storages,

            # характеристики юнитов
            'units': units,
            # оружие
            'units_dict': units_dict,

            # война
            'war': self,
            # время окончания войны
            'war_countdown': war_countdown,
            # форматированная строка текущего оставшегося времени
            'dtime_str': dtime_str,

            # сторона атаки
            'agr_dmg': agr_damage,
            # сторона обороны
            'def_dmg': def_damage,
            # разница в уроне
            'delta': def_damage - agr_damage,

            # сторона атаки - игроки
            'agr_char_list': agr_char_list,
            # сторона обороны - игроки
            'def_char_list': def_char_list,

            # класс войны
            'war_cl': War,

            'http_use': http_use,

            'graph_html': graph_html

        })


# сигнал прослушивающий создание партии, после этого формирующий таску
@receiver(post_delete, sender=EventWar)
def delete_post(sender, instance, **kwargs):
    if instance.task:
        instance.task.delete()
