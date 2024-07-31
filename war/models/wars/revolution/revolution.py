# coding=utf-8
import datetime
import json
import math
import os
import plotly.graph_objects as go
import pytz
import redis
from datetime import timedelta
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.shortcuts import redirect, render
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule, ClockedSchedule

from bill.models.bill import Bill
from gov.models.president import President
from gov.models.presidential_voting import PresidentialVoting
from gov.models.vote import Vote
from party.party import Party
from player.player import Player
from player.views.get_subclasses import get_subclasses
from player.views.timers import interval_in_seconds, format_time
from region.building.building import Building
from region.building.defences import Defences
from region.building.hospital import Hospital
from region.building.rate_building import RateBuilding
from region.models.region import Region
from skill.models.scouting import Scouting
from state.models.capital import Capital
from state.models.parliament.bulletin import Bulletin
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament_party import ParliamentParty
from state.models.parliament.parliament_voting import ParliamentVoting
from state.models.treasury import Treasury
from state.models.treasury_lock import TreasuryLock
from state.models.treasury_stock import TreasuryStock
from storage.models.auction.auction import BuyAuction
from storage.models.good import Good
from storage.models.good_lock import GoodLock
from storage.models.stock import Stock
from storage.models.storage import Storage
from storage.models.trade_offer import TradeOffer
from war.models.wars.player_damage import PlayerDamage
from war.models.wars.unit import Unit
from war.models.wars.war import War
from war.models.wars.war_side import WarSide
from region.models.terrain.terrain_modifier import TerrainModifier
from skill.models.scouting import Scouting
from skill.models.coherence import Coherence


# восстание в регионе
class Revolution(War):
    # прочность Штаба
    hq_points = models.BigIntegerField(default=0, verbose_name='Прочность Штаба')
    # стороны войны
    war_side = GenericRelation(WarSide)
    # урон в этой войне
    war_damage = GenericRelation(PlayerDamage)

    def __str__(self):
        return 'Восстание в регионе ' + getattr(self.agr_region, 'region_name')

    # Свойства класса
    class Meta:
        # abstract = True
        verbose_name = "Восстание"
        verbose_name_plural = "Восстания"

    # создаем всё, что требуется после создания войны: стороны, периодическую таску
    def after_save(self):
        # проставляем укрепления обороны
        if Defences.objects.filter(region=self.def_region).exists():
            self.hq_points = Defences.objects.get(region=self.def_region).level * 500
            self.defence_points = Defences.objects.get(region=self.def_region).level * 500
        # признак что эта минута свободна, можно создавать
        free_min = False
        # признак что для этого типа войны минута свободна
        cl_flag = False
        # текущая минута
        # minute = timezone.now().now().minute
        end_time = timezone.now() + timedelta(days=1)  # Текущее время + 24 часа

        war_classes = get_subclasses(War)
        # так как задачи крона заканчиваются в начале минуты, нужно сдвигать
        # все новые войны на минуту относительно других,
        # которые своей целью ставят этот же регион или регион агрессора
        while not free_min:
            for war_cl in war_classes:
                # если нет войны, которая объявлена одному из двух регионов
                if not war_cl.objects.filter(
                        Q(def_region=self.agr_region) | Q(def_region=self.def_region),
                        end_task__clocked__clocked_time__minute=end_time.minute,
                ).exists():
                    # отмечаем эту минуту свободной
                    cl_flag = True
                # если хоть раз нашли запись - очищаем флаг и выходим
                else:
                    cl_flag = False
                    break

            if cl_flag:
                free_min = True

            else:
                end_time = end_time + timedelta(minutes=1)

        schedule, created = CrontabSchedule.objects.get_or_create(
            minute='*',
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )

        self.task = PeriodicTask.objects.create(
            name=f'Война Revolution {self.pk}',
            task='war_round_task',
            # interval=schedule,
            crontab=schedule,
            args=json.dumps(['Revolution', self.pk, ]),
            start_time=timezone.now()
        )
        self.start_time = timezone.now()

        clocked_schedule, created = ClockedSchedule.objects.get_or_create(
            clocked_time=end_time,
        )

        self.end_task = PeriodicTask.objects.create(
            name=f'Завершение войны Revolution {self.pk}',
            task='end_war',
            clocked=clocked_schedule,
            one_off=True,
            args=json.dumps(['Revolution', self.pk]),
            start_time=timezone.now()
        )

        self.end_task.save()

        self.save()

        war_side_agr = WarSide(
            content_object=self,
            side='agr',
        )
        war_side_agr.save()

        war_side_def = WarSide(
            content_object=self,
            side='def',
        )
        war_side_def.save()

    # просчитать раунд войны
    def war_round(self):
        self.round += 1
        r = redis.StrictRedis(host='redis', port=6379, db=0)

        agr_damage = r.hget(f'{self.__class__.__name__}_{self.pk}_dmg', 'agr')
        if not agr_damage:
            agr_damage = 0
        else:
            agr_damage = int(float(agr_damage))

        def_damage = r.hget(f'{self.__class__.__name__}_{self.pk}_dmg', 'def')
        if not def_damage:
            def_damage = 0
        else:
            def_damage = int(float(def_damage))

        self.hq_points = def_damage + self.defence_points - agr_damage

        # сохраняем инфу в объектах
        for side in ['agr', 'def']:
            w_side = self.war_side.get(side=side)
            if side == 'agr':
                w_side.count = agr_damage
            else:
                w_side.count = def_damage
            w_side.save()

        # сохраняем очки урона в график
        graph = []
        timestamp = str(datetime.datetime.now().timestamp()).split('.')[0]

        if self.graph:
            graph = eval(self.graph)

            if not graph[-1][1] == self.hq_points:
                graph.append((timestamp, self.hq_points))
        else:
            graph.append((timestamp, self.hq_points))

        self.graph = str(graph)

        self.save()

        player_damage_u = []
        # сохраняем урон игроков
        for side in ['agr', 'def']:

            for fighter in [int(string) for string in r.lrange(f'{self.__class__.__name__}_{self.pk}_{side}', 0, -1)]:
                p_damage, created = PlayerDamage.objects.get_or_create(
                    content_type=ContentType.objects.get_for_model(self.__class__),
                    object_id=self.pk,
                    player=Player.objects.only("pk").get(pk=fighter),
                    side=side,
                )
                p_damage.damage = int(float(r.hget(f'{self.__class__.__name__}_{self.pk}_{side}_dmg', fighter)))

                player_damage_u.append(p_damage)

        if player_damage_u:
            PlayerDamage.objects.bulk_update(
                player_damage_u,
                fields=['damage', ],
                batch_size=len(player_damage_u)
            )

    # завершить войну
    @transaction.atomic
    def war_end(self):
        self.war_round()

        pk = self.task.pk
        end_pk = self.end_task.pk

        self.task = None
        self.end_task = None

        self.running = False
        self.end_time = timezone.now()
        self.save()

        PeriodicTask.objects.filter(pk=pk).delete()
        PeriodicTask.objects.filter(pk=end_pk).delete()

        # ЕСЛИ ПОБЕДИЛ АТАКУЮЩИЙ:
        if not self.hq_points < 0:
            return

        tres = None

        # Захват Казны врага
        if Treasury.objects.filter(region=self.def_region, deleted=False).exists():
            tres = Treasury.objects.get(region=self.def_region, deleted=False)

        # удаляем партии и кандидатов в презы этого рега
        ParliamentParty.objects.filter(party__in=Party.objects.filter(region=self.def_region)).delete()
        DeputyMandate.objects.filter(party__in=Party.objects.filter(region=self.def_region)).delete()
        Bulletin.objects.filter(party__in=Party.objects.filter(region=self.def_region)).delete()
        # если есть гос
        if self.def_region.state:
            # если есть през
            if President.objects.filter(state=self.def_region.state).exists():
                # если идут его выборы
                if PresidentialVoting.objects.filter(running=True, president=President.objects.get(
                        state=self.def_region.state)).exists():
                    # выборы
                    voting = PresidentialVoting.objects.get(running=True, president=President.objects.get(
                        state=self.def_region.state))

                    for candidate in voting.candidates.all():
                        # если партия кандидата из нашего региона - удаляем его
                        if candidate.party and candidate.party.region == self.def_region:
                            voting.candidates.remove(candidate)

                    voting.save()

        # удаляем все ЗП, связанные с регионом
        # зп, содержащие регион
        bills_req_list = ['ChangeTaxes', 'ExploreResources', 'Construction', 'StartWar', 'Independence']
        bills_classes = get_subclasses(Bill)
        for type in bills_classes:
            if type.__name__ in bills_req_list:
                if type.objects.filter(running=True, region=self.def_region).exists():
                    for bill in type.objects.filter(running=True, region=self.def_region):
                        # отмечаем отмененным
                        task = bill.task
                        bill.task = None
                        bill.type = 'cn'
                        bill.running = False
                        bill.voting_end = timezone.now()
                        bill.save()

                        task.delete()

        # 1. Присоединение региона
        # 1.1 Если столичный регион
        if Capital.objects.filter(state=self.def_region.state, region=self.def_region).exists():

            # 1.1.1 Если у врага еще есть регионы
            if Region.objects.filter(state=self.def_region.state).exclude(pk=self.def_region.pk).exists():
                top_hospital = Hospital.objects.filter(
                    region__in=Region.objects.filter(state=self.def_region.state).exclude(pk=self.def_region.pk)
                ).order_by('-top').first()
                # находим лучший регион по медицине, ставим столицу там
                capital = Capital.objects.get(state=self.def_region.state, region=self.def_region)
                capital.region = top_hospital.region
                capital.save()
                # переносим казну туда же
                if tres:
                    tres.region = top_hospital.region
                    tres.save()

            # 1.1.2 Если это последний регион врага
            else:
                # роспуск правительства:
                # 1. лидера (если есть)
                # 2. парламента (если есть)
                # 3. стольни
                # 4. казны
                self.def_region.state.dissolution()

        # 3. Разрушение зданий
        components = {}
        building_classes = get_subclasses(Building)
        for building_cl in building_classes:
            if building_cl.objects.filter(region=self.def_region).exists():
                building = building_cl.objects.get(region=self.def_region)

            else:
                building = building_cl(region=self.def_region)

            setattr(building, 'level', math.ceil(getattr(building, 'level') / 2))
            building.save()

            # если это рейтинговое строение
            if RateBuilding in building_cl.__bases__:
                # пересчитаем рейтинг
                building_cl.recount_rating()

            elif building_cl.__name__ == 'PowerPlant':
                for building_sub_cl in building_classes:
                    if RateBuilding in building_sub_cl.__bases__:
                        # пересчитаем рейтинг
                        building_sub_cl.recount_rating()


        war_classes = get_subclasses(War)
        # 4. Если идут другие войны за этот же рег - завершить
        for other_war_cl in war_classes:
            # если есть ДРУГИЕ войны
            if other_war_cl.objects.filter(running=True, def_region=self.def_region).exclude(pk=self.pk).exists():
                # каждый из них завершить
                for other_war in other_war_cl.objects.filter(running=True, def_region=self.def_region).exclude(pk=self.pk):
                    pk = other_war.task.pk
                    other_war.task = None
                    other_war.running = False
                    other_war.end_time = timezone.now()
                    other_war.save()
                    PeriodicTask.objects.filter(pk=pk).delete()

        # если есть активные войны из этого региона на другие
        for other_war_cl in war_classes:
            if other_war_cl.objects.filter(running=True, agr_region=self.def_region).exists():
                # каждый из них завершить
                for other_war in other_war_cl.objects.filter(running=True, agr_region=self.def_region):
                    pk = other_war.task.pk
                    other_war.task = None
                    other_war.running = False
                    other_war.end_time = timezone.now()
                    other_war.save()
                    PeriodicTask.objects.filter(pk=pk).delete()
                    

        # 1.1.6 заменяем у захваченного региона государство
        Region.objects.filter(pk=self.def_region.pk).update(
            cash_tax=0,
            oil_tax=0,
            ore_tax=0,
            trade_tax=0,
            state=None,
            peace_date=timezone.now() + datetime.timedelta(days=14)
        )

    def get_attrs(self):
        return {
            'hq_points': self.hq_points,
        }

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
            agr_damage = int(float(agr_damage))

        def_damage = r.hget(f'{self.__class__.__name__}_{self.pk}_dmg', 'def')
        if not def_damage:
            def_damage = 0
        else:
            def_damage = int(float(def_damage))

        war_countdown = interval_in_seconds(
            object=self,
            start_fname='start_time',
            end_fname=None,
            delay_in_sec=86400
        )

        dtime_str = format_time(war_countdown)

        agr_terrains = self.agr_region.terrain.all()
        def_terrains = self.def_region.terrain.all()
        terrain_list = []

        for terrain in agr_terrains:
            terrain_list.append(terrain)

        for terrain in def_terrains:
            if not terrain in terrain_list:
                terrain_list.append(terrain)

        modifiers_dict = {}
        # модификаторы урона для этого набора рельефов
        modifiers = TerrainModifier.objects.filter(terrain__in=terrain_list)

        for modifier in modifiers:
            if modifier.unit.pk in modifiers_dict.keys():
                modifiers_dict[modifier.unit.pk] = modifiers_dict[modifier.unit.pk] * modifier.modifier
            else:
                modifiers_dict[modifier.unit.pk] = modifier.modifier

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

        # знание местности
        scouting_perk = 0
        if Scouting.objects.filter(player=player, level__gt=0).exists():
            unit_dmg = Scouting.objects.get(player=player).apply({'dmg': 100})
            # если перк не применился, значит, игрок находится менее суток в реге, учитывать не надо
            if unit_dmg > 100:
                scouting_perk = Scouting.objects.get(player=player).level

        # Слаженность
        coherence_perk = False
        if Coherence.objects.filter(player=player, level__gt=0).exists():
            coherence_perk = True

        # --------------------------------------------------------------------------------------------
        data = []
        graph_html = None
        if self.graph:
            data = eval(self.graph)

        if data:
            # Разделите список на два отдельных списка: timestamps и scores
            timestamps, scores = zip(*data)

            # Преобразуйте значения timestamps в объекты datetime
            timestamps = [datetime.datetime.fromtimestamp(int(timestamp)).astimezone(tz=pytz.timezone(player.time_zone))
                          for timestamp in timestamps]

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
            # модификаторы урона для юнитов
            'modifiers_dict': modifiers_dict,
            # оружие
            'units_dict': units_dict,

            # война
            'war': self,
            # модификаторы рельефа
            'terrains': terrain_list,
            # перки
            'coherence_perk': coherence_perk,
            'scouting_perk': scouting_perk,
            # время окончания войны
            'war_countdown': war_countdown,
            # форматированная строка текущего оставшегося времени
            'dtime_str': dtime_str,

            # сторона атаки
            'agr_dmg': agr_damage,
            # сторона обороны
            'def_dmg': def_damage,
            # разница в уроне
            'delta': def_damage + self.defence_points - agr_damage,

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
@receiver(post_delete, sender=Revolution)
def delete_post(sender, instance, **kwargs):
    if instance.task:
        instance.task.delete()


# сигнал прослушивающий создание
@receiver(post_save, sender=Revolution)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.after_save()
