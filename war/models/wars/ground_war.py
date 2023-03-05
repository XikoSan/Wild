# coding=utf-8
import json
import math
import datetime
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule

from player.views.get_subclasses import get_subclasses
from region.building.building import Building
from region.building.hospital import Hospital
from region.region import Region
from state.models.treasury import Treasury
from state.models.treasury_lock import TreasuryLock
from storage.models.storage import Storage
from war.models.squads.heavy_vehicle import HeavyVehicle
from war.models.squads.infantry import Infantry
from war.models.squads.light_vehicle import LightVehicle
from war.models.squads.recon import Recon
from war.models.wars.war import War
from war.models.wars.war_side import WarSide
from storage.models.auction.auction import BuyAuction
from state.models.parliament.parliament_party import ParliamentParty
from party.party import Party
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.bulletin import Bulletin
from state.models.parliament.parliament_voting import ParliamentVoting
from gov.models.presidential_voting import PresidentialVoting
from party.primaries.primaries_leader import PrimariesLeader
from gov.models.vote import Vote
from bill.models.bill import Bill
from storage.models.good_lock import GoodLock
from storage.models.trade_offer import TradeOffer
from region.building.rate_building import RateBuilding
from state.models.capital import Capital
from gov.models.president import President
from region.building.defences import Defences
from skill.models.scouting import Scouting


# класс наземной войны
class GroundWar(War):
    using_units = ['rifle', 'ifv', 'antitank', 'tank', 'drone']
    squads_list = ['infantry', 'lightvehicle', 'heavyvehicle', 'recon']
    # прочность Штаба
    hq_points = models.BigIntegerField(default=0, verbose_name='Прочность Штаба')
    # стороны войны
    war_side = GenericRelation(WarSide)

    # отряды разведки
    recon = GenericRelation(Recon)
    # отряды пихоты
    infantry = GenericRelation(Infantry)
    # отряды легкой бронетехники
    lightvehicle = GenericRelation(LightVehicle)
    # отряды тяжелой бронетехники
    heavyvehicle = GenericRelation(HeavyVehicle)

    def __str__(self):
        return 'Наземная: ' + getattr(self.agr_region, 'region_name') + ' - ' + getattr(self.def_region, 'region_name')

    # Свойства класса
    class Meta:
        verbose_name = "Наземная война"
        verbose_name_plural = "Наземные войны"

    # создаем всё, что требуется после создания войны: стороны, периодическую таску
    def after_save(self):
        # проставляем укрпления обороны
        if Defences.objects.filter(region=self.def_region).exists():
            self.hq_points = Defences.objects.get(region=self.def_region).level * 1000
        # признак что эта минута свободна, можно создавать
        free_min = False
        # признак что для этого типа войны минута свободна
        cl_flag = False
        # текущая минута
        minute = timezone.now().now().minute

        war_classes = get_subclasses(War)
        # так как задачи крона заканчиваются в начале минуты, нужно сдвигать
        # все новые войны на минуту относительно других,
        # которые своей целью ставят этот же регион или регион агрессора
        while not free_min:
            for war_cl in war_classes:
                # если нет войны, которая объявлена одному из двух регионов
                if not war_cl.objects.filter(
                        Q(def_region=self.agr_region) | Q(def_region=self.def_region),
                        task__crontab__minute=str(minute)
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
                minute += 1

        schedule, created = CrontabSchedule.objects.get_or_create(
            minute=str(minute),
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )

        self.task = PeriodicTask.objects.create(
            name=f'Война GroundWar {self.pk}',
            task='war_round_task',
            # interval=schedule,
            crontab=schedule,
            args=json.dumps(['GroundWar', self.pk, ]),
            start_time=timezone.now()
        )
        self.start_time = timezone.now() + datetime.timedelta(minutes=minute-timezone.now().minute)
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
        self.round_log = '<div class="row" align="center">Фаза войны: ' + str(self.round) + '</div>'

        # получаем стороны войны
        agr_side = self.war_side.get(side='agr', object_id=self.pk)
        def_side = self.war_side.get(side='def', object_id=self.pk)

        squads_list = self.squads_list
        squads_dict = {}

        for squad_type in squads_list:
            # сразу отмечаем что в бою
            getattr(self, squad_type).filter(object_id=self.pk, deleted=False, deployed=False).update(deployed=True)
            # получаем все отряды текущего типа этой войны
            squads_dict[squad_type] = getattr(self, squad_type).filter(object_id=self.pk, deleted=False)

        units_dict = {
            'agr': {},
            'def': {}
        }
        types_damage_dict = {
            'agr': {},
            'def': {}
        }

        damage_dict = {
            'agr': {},
            'def': {}
        }
        # по каждому типу отрядов получаем урон, наносимый ими
        for squad_type in squads_list:
            # damage_dict[squad_type] = {}
            # если есть хоть один отряд
            if squads_dict[squad_type]:
                # по каждому отряду типа
                for squad in squads_dict[squad_type]:
                    # damage_dict[squad_type][squad.side] = {}
                    # по каждому юниту отряда
                    for unit in getattr(squad, 'specs').keys():
                        # vvvvvvvvvv логи vvvvvvvvvv
                        if getattr(squad, 'specs')[unit]['name'] in units_dict[squad.side]:
                            units_dict[squad.side][getattr(squad, 'specs')[unit]['name']] += getattr(squad, unit)
                        else:
                            units_dict[squad.side][getattr(squad, 'specs')[unit]['name']] = getattr(squad, unit)
                        # ^^^^^^^^^^ логи ^^^^^^^^^^

                        # для каждого типа юнитов, по которому этот юнит может бить
                        for target_type in getattr(squad, 'specs')[unit]['damage'].keys():

                            # vvv--- знание местности ---vvv
                            if Scouting.objects.filter(player=squad.owner, level__gt=0).exists():
                                scouting = Scouting.objects.get(player=squad.owner)

                                sum = getattr(squad, unit) * \
                                      getattr(squad, 'specs')[unit][
                                          'damage'][
                                          target_type]

                                sq_dmg = scouting.apply({'sum': sum})

                            else:
                                sq_dmg = getattr(squad, unit) * \
                                                getattr(squad, 'specs')[unit][
                                                    'damage'][
                                                    target_type]
                            # ^^^--- знание местности ---^^^

                            if target_type in damage_dict[squad.side]:
                                damage_dict[squad.side][target_type] += sq_dmg

                            else:
                                damage_dict[squad.side][target_type] = sq_dmg

                            # vvvvvvvvvv логи vvvvvvvvvv
                            if self.squads_dict[target_type] in types_damage_dict[squad.side]:
                                types_damage_dict[squad.side][self.squads_dict[target_type]] += sq_dmg
                            else:
                                types_damage_dict[squad.side][self.squads_dict[target_type]] = sq_dmg
                            # ^^^^^^^^^^ логи ^^^^^^^^^^

        # vvvvvvvvvv логи vvvvvvvvvv
        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Силы атакующих:</div>'

        if units_dict['agr']:
            self.round_log += '<div class="row" align="center"><table><tr>'

            for unit in units_dict['agr'].keys():
                self.round_log += '<th>' + str(unit) + '</th>'
            self.round_log += '</tr><tr>'

            for unit in units_dict['agr'].keys():
                self.round_log += '<td>' + str(units_dict['agr'][unit]) + '</td>'
            self.round_log += '</tr></table></div>'

        else:
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">нет войск</div>'

        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Силы обороны:</div>'

        if units_dict['def']:
            self.round_log += '<div class="row" align="center"><table><tr>'

            for unit in units_dict['def'].keys():
                self.round_log += '<th>' + str(unit) + '</th>'
            self.round_log += '</tr><tr>'

            for unit in units_dict['def'].keys():
                self.round_log += '<td>' + str(units_dict['def'][unit]) + '</td>'
            self.round_log += '</tr></table></div>'

        else:
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">нет войск</div>'

        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Урон атакующих по родам войск:</div>'

        if types_damage_dict['agr']:
            self.round_log += '<div class="row" align="center"><table><tr>'

            for unit in types_damage_dict['agr'].keys():
                self.round_log += '<th>' + str(unit) + '</th>'
            self.round_log += '</tr><tr>'

            for unit in types_damage_dict['agr'].keys():
                self.round_log += '<td>' + str(types_damage_dict['agr'][unit]) + '</td>'

            self.round_log += '</tr></table></div>'

        else:
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">нет урона</div>'

        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Урон оброны по родам войск:</div>'

        if types_damage_dict['def']:
            self.round_log += '<div class="row" align="center"><table><tr>'

            for unit in types_damage_dict['def'].keys():
                self.round_log += '<th>' + str(unit) + '</th>'
            self.round_log += '</tr><tr>'

            for unit in types_damage_dict['def'].keys():
                self.round_log += '<td>' + str(types_damage_dict['def'][unit]) + '</td>'

            self.round_log += '</tr></table></div>'

        else:
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">нет урона</div>'
        # ^^^^^^^^^^ логи ^^^^^^^^^^

        hp_dict = {}

        hp_log_dict = {
            'agr': {},
            'def': {}
        }

        for squad_type in squads_list:
            hp_dict[squad_type] = {}
            hp_dict[squad_type]['agr'] = 0
            hp_dict[squad_type]['def'] = 0

        # по каждому типу отрядов получаем здоровье
        for squad_type in squads_list:
            # если есть хоть один отряд
            if squads_dict[squad_type]:
                if squads_dict[squad_type]:
                    # по каждому отряду типа
                    for squad in squads_dict[squad_type]:
                        # по каждому юниту отряда
                        for unit in getattr(squad, 'specs').keys():
                            if squad.side in hp_dict[squad_type]:
                                hp_dict[squad_type][squad.side] += getattr(squad, unit) * getattr(squad, 'specs')[unit][
                                    'hp']
                            else:
                                hp_dict[squad_type][squad.side] = getattr(squad, unit) * getattr(squad, 'specs')[unit][
                                    'hp']

                            # vvvvvvvvvv логи vvvvvvvvvv
                            if self.squads_dict[squad_type] in hp_log_dict[squad.side]:
                                hp_log_dict[squad.side][self.squads_dict[squad_type]] += getattr(squad, unit) * \
                                                                                         getattr(squad, 'specs')[unit][
                                                                                             'hp']
                            else:
                                hp_log_dict[squad.side][self.squads_dict[squad_type]] = getattr(squad, unit) * \
                                                                                        getattr(squad, 'specs')[unit][
                                                                                            'hp']
                            # ^^^^^^^^^^ логи ^^^^^^^^^^

        # vvvvvvvvvv логи vvvvvvvvvv
        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Прочность атакующих по родам войск:</div>'

        if hp_log_dict['agr']:
            self.round_log += '<div class="row" align="center"><table><tr>'

            for squad_type in hp_log_dict['agr'].keys():
                self.round_log += '<th>' + str(squad_type) + '</th>'
            self.round_log += '</tr><tr>'

            for squad_type in hp_log_dict['agr'].keys():
                self.round_log += '<td>' + str(hp_log_dict['agr'][squad_type]) + '</td>'

            self.round_log += '</tr></table></div>'

        else:
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">нет войск</div>'

        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Прочность обороны по родам войск:</div>'

        if hp_log_dict['def']:
            self.round_log += '<div class="row" align="center"><table><tr>'

            for squad_type in hp_log_dict['def'].keys():
                self.round_log += '<th>' + str(squad_type) + '</th>'
            self.round_log += '</tr><tr>'

            for squad_type in hp_log_dict['def'].keys():
                self.round_log += '<td>' + str(hp_log_dict['def'][squad_type]) + '</td>'

            self.round_log += '</tr></table></div>'

        else:
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">нет войск</div>'
        # ^^^^^^^^^^ логи ^^^^^^^^^^

        # =============================================================================================================

        # отряды получают урон друг по другу
        new_hp_dict = {}
        free_dmg = {}

        new_hp_log_dict = {
            'agr': {},
            'def': {}
        }

        for squad_type in squads_list:
            agr_damage = 0
            def_damage = 0
            new_hp_dict[squad_type] = {}
            free_dmg[squad_type] = {}

            if squad_type in damage_dict['agr']:
                def_damage += damage_dict['agr'][squad_type]

            if squad_type in damage_dict['def']:
                agr_damage += damage_dict['def'][squad_type]

            # считаем, сколько урона пройдет по укреплениям
            if def_damage > hp_dict[squad_type]['def']:
                free_dmg[squad_type]['agr'] = def_damage - hp_dict[squad_type]['def']
            else:
                free_dmg[squad_type]['agr'] = 0

            # считаем, сколько хп останется у отрядов в целом

            new_hp_dict[squad_type]['agr'] = hp_dict[squad_type]['agr'] - agr_damage
            new_hp_dict[squad_type]['def'] = hp_dict[squad_type]['def'] - def_damage

            new_hp_log_dict['agr'][self.squads_dict[squad_type]] = hp_dict[squad_type]['agr'] - agr_damage
            new_hp_log_dict['def'][self.squads_dict[squad_type]] = hp_dict[squad_type]['def'] - def_damage

        # vvvvvvvvvv логи vvvvvvvvvv
        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Стороны боя наносят урон друг другу</div>'
        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Прочность атакующих после нанесения урона:</div>'

        if new_hp_log_dict['agr']:
            self.round_log += '<div class="row" align="center"><table><tr>'

            for squad_type in new_hp_log_dict['agr'].keys():
                self.round_log += '<th>' + str(squad_type) + '</th>'
            self.round_log += '</tr><tr>'

            for squad_type in new_hp_log_dict['agr'].keys():
                self.round_log += '<td>' + str(new_hp_log_dict['agr'][squad_type]) + '</td>'

            self.round_log += '</tr></table></div>'

        else:
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">нет войск</div>'

        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Прочность обороны после нанесения урона:</div>'

        if new_hp_log_dict['def']:
            self.round_log += '<div class="row" align="center"><table><tr>'

            for squad_type in new_hp_log_dict['def'].keys():
                self.round_log += '<th>' + str(squad_type) + '</th>'
            self.round_log += '</tr><tr>'

            for squad_type in new_hp_log_dict['def'].keys():
                self.round_log += '<td>' + str(new_hp_log_dict['def'][squad_type]) + '</td>'

            self.round_log += '</tr></table></div>'

        else:
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">нет войск</div>'

        # ^^^^^^^^^^ логи ^^^^^^^^^^

        # если урон у атакующих остался - его получают укрепления
        agr_damage_sum = 0
        for squad_type in squads_list:
            if free_dmg[squad_type]['agr'] > 0:
                agr_damage_sum += free_dmg[squad_type]['agr']

        # ==============================================================================================================
        # разведки у атаки
        drone_agr = 0
        # разведки у защиты
        drone_def = 0

        lost_per_log_dict = {
            'agr': {},
            'def': {}
        }

        surv_log_dict = {
            'agr': {},
            'def': {}
        }

        # считаем, сколько юнитов полегло
        for squad_type in squads_list:
            static_class = ContentType.objects.get(app_label="war", model=squad_type).model_class()

            # узнаем процент выживших новых отрядов атаки:
            if hp_dict[squad_type]['agr'] == 0:
                lost_perc_agr = 0
                lost_per_log_dict['agr'][self.squads_dict[squad_type]] = 0
            else:
                lost_perc_agr = new_hp_dict[squad_type]['agr'] / hp_dict[squad_type]['agr']
                lost_per_log_dict['agr'][self.squads_dict[squad_type]] = int(
                    new_hp_dict[squad_type]['agr'] / hp_dict[squad_type]['agr'] * 100)

            # узнаем процент выживших новых отрядов защиты:
            if hp_dict[squad_type]['def'] == 0:
                lost_perc_def = 0
                lost_per_log_dict['def'][self.squads_dict[squad_type]] = 0
            else:
                lost_perc_def = new_hp_dict[squad_type]['def'] / hp_dict[squad_type]['def']
                lost_per_log_dict['def'][self.squads_dict[squad_type]] = int(
                    new_hp_dict[squad_type]['def'] / hp_dict[squad_type]['def'] * 100)

            # занулить юнитов сторон боя
            for unit in getattr(static_class, 'specs').keys():
                setattr(agr_side, unit, 0)
                setattr(def_side, unit, 0)

            # по каждому отряду типа
            for squad in squads_dict[squad_type]:
                # по каждому юниту отряда
                has_units = False
                for unit in getattr(squad, 'specs').keys():
                    if squad.side == 'agr':
                        if getattr(squad, unit) * lost_perc_agr < 0:
                            setattr(squad, unit, 0)
                        else:
                            if int(getattr(squad, unit) * lost_perc_agr) > 0:
                                has_units = True
                                if unit == 'drone':
                                    drone_agr += int(getattr(squad, unit) * lost_perc_agr)

                            setattr(squad, unit, int(getattr(squad, unit) * lost_perc_agr))
                        # прописываем в стороны боя, чтобы можно было выводить
                        setattr(agr_side, unit, int(getattr(agr_side, unit) + getattr(squad, unit)))

                    else:
                        if getattr(squad, unit) * lost_perc_def < 0:
                            setattr(squad, unit, 0)
                        else:
                            if int(getattr(squad, unit) * lost_perc_def) > 0:
                                has_units = True
                                if unit == 'drone':
                                    drone_def += int(getattr(squad, unit) * lost_perc_def)

                            setattr(squad, unit, int(getattr(squad, unit) * lost_perc_def))
                        # прописываем в стороны боя, чтобы можно было выводить
                        setattr(def_side, unit, int(getattr(def_side, unit) + getattr(squad, unit)))

                    if getattr(squad, 'specs')[unit]['name'] in surv_log_dict[squad.side]:
                        surv_log_dict[squad.side][getattr(squad, 'specs')[unit]['name']] += getattr(squad, unit)
                    else:
                        surv_log_dict[squad.side][getattr(squad, 'specs')[unit]['name']] = getattr(squad, unit)

                # если все полегли
                if not has_units:
                    squad.destroy = timezone.now()
                    squad.deleted = True
                # сохраняем отряд с новым числом юнитов
                squad.save()

        # vvvvvvvvvv логи vvvvvvvvvv
        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Устанавливаем процент выживших по родам войск</div>'
        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Процент выживших среди атакующих:</div>'

        if lost_per_log_dict['agr']:
            self.round_log += '<div class="row" align="center"><table><tr>'

            for squad_type in lost_per_log_dict['agr'].keys():
                self.round_log += '<th>' + str(squad_type) + '</th>'
            self.round_log += '</tr><tr>'

            for squad_type in lost_per_log_dict['agr'].keys():
                self.round_log += '<td>' + str(lost_per_log_dict['agr'][squad_type]) + '%</td>'

            self.round_log += '</tr></table></div>'

        else:
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">нет войск</div>'

        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Процент выживших среди обороны:</div>'

        if lost_per_log_dict['def']:
            self.round_log += '<div class="row" align="center"><table><tr>'

            for squad_type in lost_per_log_dict['def'].keys():
                self.round_log += '<th>' + str(squad_type) + '</th>'
            self.round_log += '</tr><tr>'

            for squad_type in lost_per_log_dict['def'].keys():
                self.round_log += '<td>' + str(lost_per_log_dict['def'][squad_type]) + '%</td>'

            self.round_log += '</tr></table></div>'

        else:
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">нет войск</div>'

        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Количество выживших войск в этом раунде</div>'
        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Силы атакующих:</div>'

        if surv_log_dict['agr']:
            self.round_log += '<div class="row" align="center"><table><tr>'

            for unit in surv_log_dict['agr'].keys():
                self.round_log += '<th>' + str(unit) + '</th>'
            self.round_log += '</tr><tr>'

            for unit in surv_log_dict['agr'].keys():
                self.round_log += '<td>' + str(surv_log_dict['agr'][unit]) + '</td>'

            self.round_log += '</tr></table></div>'

        else:
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">нет войск</div>'

        self.round_log += '<hr>'
        self.round_log += '<div class="row" align="center" style="margin-top: 10px">Силы обороны:</div>'

        if surv_log_dict['def']:
            self.round_log += '<div class="row" align="center"><table><tr>'

            for unit in surv_log_dict['def'].keys():
                self.round_log += '<th>' + str(unit) + '</th>'
            self.round_log += '</tr><tr>'

            for unit in surv_log_dict['def'].keys():
                self.round_log += '<td>' + str(surv_log_dict['def'][unit]) + '</td>'

            self.round_log += '</tr></table></div>'

        else:
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">нет войск</div>'

        if agr_damage_sum:
            self.round_log += '<hr>'
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">Не распределённый по родам войск урон атакующих:</div>'
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">' + str(
                agr_damage_sum) + '</div>'
        # ^^^^^^^^^^ логи ^^^^^^^^^^

        agr_side.save()
        def_side.save()

        if not drone_def and drone_agr > 0:
            self.recon_balance = 100
        elif not drone_def and not drone_agr:
            self.recon_balance = 1
        else:
            self.recon_balance = drone_agr / drone_def

        if agr_damage_sum > self.hq_points:
            self.hq_points -= agr_damage_sum
            self.war_end()
        else:
            self.hq_points -= agr_damage_sum

        if self.round == 24:
            self.war_end()

        self.save()

    # завершить войну
    @transaction.atomic
    def war_end(self):
        pk = self.task.pk
        self.task = None
        self.running = False
        self.end_time = timezone.now()
        self.save()
        PeriodicTask.objects.filter(pk=pk).delete()


        # ЕСЛИ ПОБЕДИЛ АТАКУЮЩИЙ:
        if not self.hq_points <= 0:
            return
        # todo: сделать чтобы во время войны нельзя было работать с Наличными на Складе

        tres = None
        agr_tres = Treasury.objects.get(state=self.agr_region.state)

        # Захват Казны врага
        if Treasury.objects.filter(region=self.def_region, deleted=False).exists():
            tres = Treasury.objects.get(region=self.def_region, deleted=False)
            # половина сгорит, ещё половину - разграбляем
            agr_tres.cash += math.ceil(getattr(tres, 'cash') / 4)
            # сжигаем оставшееся
            setattr(tres, 'cash', math.ceil(getattr(tres, 'cash') / 4))

            for mode in Storage.types.keys():
                for unit in getattr(Storage, mode).keys():
                    # половина сгорит, ещё половину - разграбляем
                    setattr(agr_tres, unit, getattr(agr_tres, unit) + math.ceil(getattr(tres, unit) / 4))
                    # сжигаем оставшееся
                    setattr(tres, unit, math.ceil(getattr(tres, unit) / 4))

            # если есть блокировки - их тоже захватываем
            if TreasuryLock.objects.filter(lock_treasury=tres, deleted=False).exists():
                for lock in TreasuryLock.objects.filter(lock_treasury=tres, deleted=False):
                    setattr(agr_tres, lock.lock_good,
                            getattr(agr_tres, lock.lock_good) + math.ceil(lock.lock_count / 4))
                    lock.deleted = True
                    lock.save()
                    # закупки ресурсов отменяем
                    if BuyAuction.actual.filter(treasury_lock=lock).exists():
                        auction = BuyAuction.actual.get(treasury_lock=lock)
                        # и таску удаляет, и метку ставит
                        auction.delete_task()

            agr_tres.save()
            tres.save()

        # удаляем партии и кандидатов в презы этого рега
        ParliamentParty.objects.filter(party__in=Party.objects.filter(region=self.def_region)).delete()
        DeputyMandate.objects.filter(party__in=Party.objects.filter(region=self.def_region)).delete()
        Bulletin.objects.filter(party__in=Party.objects.filter(region=self.def_region)).delete()
        # если есть гос
        if self.def_region.state:
            # если есть през
            if President.objects.filter(state=self.def_region.state).exists():
                # если идут его выборы
                if PresidentialVoting.objects.filter(running=True, president=President.objects.get(state=self.def_region.state)).exists():
                    # выборы
                    voting = PresidentialVoting.objects.get(running=True, president=President.objects.get(state=self.def_region.state))
                    # находим лидеров праймериз из этого рега
                    prim_leaders = PrimariesLeader.objects.filter(party__in=Party.objects.filter(region=self.def_region))
                    # todo: а что если лидер праймериз сменится во время выборов, перед окончанием войны? сделать кандидатов отдельной моделью, в которой будет хранится партия, от которой они
                    for prim_leader in prim_leaders:
                        voting.candidates.remove(prim_leader.leader)
                        # удаляем голоса за них
                        Vote.objects.filter(voting=voting, challenger=prim_leader.leader).delete()

                    voting.save()

        # удаляем все ЗП, связанные с регионом
        # зп, содержащие регион
        bills_req_list = ['ChangeTaxes', 'ExploreResources', 'Construction', 'StartWar']
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

        # 1.1.6 заменяем у захваченного региона государство
        self.def_region.state = self.agr_region.state

        # 2. Снос складов
        tres = None

        # Захват Казны врага
        if Storage.actual.filter(region=self.def_region).exists():
            storages = Storage.actual.filter(region=self.def_region)
            for storg in storages:
                # половина сгорит, ещё половину - разграбляем
                agr_tres.cash += math.ceil(getattr(storg, 'cash') / 4)
                # сжигаем оставшееся
                setattr(storg, 'cash', math.ceil(getattr(storg, 'cash') / 4))

                for mode in Storage.types.keys():
                    for unit in getattr(Storage, mode).keys():
                        # половина сгорит, ещё половину - разграбляем
                        setattr(agr_tres, unit, getattr(agr_tres, unit) + math.ceil(getattr(storg, unit) / 4))
                        # сжигаем оставшееся
                        setattr(storg, unit, math.ceil(getattr(storg, unit) / 4))

                # если есть блокировки - их тоже захватываем
                if GoodLock.actual.filter(lock_storage=storg).exists():
                    for lock in GoodLock.actual.filter(lock_storage=storg):
                        setattr(agr_tres, lock.lock_good,
                                getattr(agr_tres, lock.lock_good) + math.ceil(lock.lock_count / 4))
                        lock.deleted = True
                        lock.save()
                        # связанное торговое предложение
                        if lock.lock_offer:
                            lock.lock_offer.accept_date = timezone.now()
                            lock.lock_offer.deleted = True
                            lock.lock_offer.save()

                agr_tres.save()
                storg.save()

        # 3. Разрушение зданий
        building_classes = get_subclasses(Building)
        for building_cl in building_classes:
            if building_cl.objects.filter(region=self.def_region).exists():
                building = building_cl.objects.get(region=self.def_region)

            else:
                building = building_cl(region=self.def_region)

            level_before = getattr(building, 'level')

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

            for type in bills_classes:
                if type.__name__ == 'Construction':
                    for res in getattr(type, building_cl.__name__)['resources'].keys():
                        res_count = getattr(type, building_cl.__name__)['resources'][res] * ( level_before - getattr(building, 'level'))

                        setattr(agr_tres, res,
                                getattr(agr_tres, res) + res_count)

        agr_tres.save()

        war_classes = get_subclasses(War)
        # 4. Если идут другие войны этих же госов за этот же рег - завершить
        for other_war_cl in war_classes:
            # если есть ДРУГИЕ войны такого типа этих же регионов
            if other_war_cl.objects.filter(running=True, agr_region=self.agr_region, def_region=self.def_region).exclude(pk=self.pk).exists():
                # каждый из них завершить
                for other_war in other_war_cl.objects.filter(running=True, agr_region=self.agr_region, def_region=self.def_region).exclude(pk=self.pk):

                    pk = other_war.task.pk
                    other_war.task = None
                    other_war.running = False
                    other_war.end_time = timezone.now()
                    other_war.save()
                    PeriodicTask.objects.filter(pk=pk).delete()

        for other_war_cl in war_classes:
            # если есть ДРУГИЕ войны такого типа этого же агрессора
            if other_war_cl.objects.filter(running=True, agr_region__state=self.agr_region.state,
                                           def_region=self.def_region).exclude(pk=self.pk).exists():
                # каждый из них завершить
                for other_war in other_war_cl.objects.filter(running=True, agr_region__state=self.agr_region.state,
                                                             def_region=self.def_region).exclude(pk=self.pk):
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

        self.def_region.save()

    def get_attrs(self):
        return {
            'hq_points': self.hq_points,
        }


# сигнал прослушивающий создание партии, после этого формирующий таску
@receiver(post_delete, sender=GroundWar)
def delete_post(sender, instance, **kwargs):
    if instance.task:
        instance.task.delete()


# сигнал прослушивающий создание
@receiver(post_save, sender=GroundWar)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.after_save()
