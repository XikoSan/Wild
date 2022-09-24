# coding=utf-8
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django_celery_beat.models import PeriodicTask

from war.models.squads.heavy_vehicle import HeavyVehicle
from war.models.squads.infantry import Infantry
from war.models.squads.light_vehicle import LightVehicle
from war.models.squads.recon import Recon
from war.models.wars.war import War
from war.models.wars.war_side import WarSide


# класс ивентовой войны
class EventWar(War):
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
        return 'Тестовая война в регионе ' + getattr(self.agr_region, 'region_name')

    # Свойства класса
    class Meta:
        verbose_name = "Тестовая война"
        verbose_name_plural = "Тестовые войны"

    # просчитать раунд войны
    def war_round(self):

        self.round += 1

        # получаем стороны войны
        agr_side = self.war_side.get(side='agr', object_id=self.pk)
        def_side = self.war_side.get(side='def', object_id=self.pk)

        squads_list = self.squads_list
        squads_dict = {}

        for squad_type in squads_list:
            # получаем все отряды текущего типа этой войны
            squads_dict[squad_type] = getattr(self, squad_type).filter(object_id=self.pk, deleted=False)

        from player.logs.print_log import log
        log('squads_dict')
        log(squads_dict)

        damage_dict = {}
        # по каждому типу отрядов получаем урон, наносимый ими
        for squad_type in squads_list:
            damage_dict[squad_type] = {}
            # если есть хоть один отряд
            if squads_dict[squad_type]:
                # по каждому отряду типа
                for squad in squads_dict[squad_type]:
                    damage_dict[squad_type][squad.side] = {}
                    # по каждому юниту отряда
                    for unit in getattr(squad, 'specs').keys():
                        # для каждого типа юнитов, по которому этот юнит может бить
                        for target_type in getattr(squad, 'specs')[unit]['damage'].keys():
                            if target_type in damage_dict[squad_type][squad.side]:
                                damage_dict[squad_type][squad.side][target_type] += getattr(squad, unit) * \
                                                                                    getattr(squad, 'specs')[unit][
                                                                                        'damage'][
                                                                                        target_type]
                            else:
                                damage_dict[squad_type][squad.side][target_type] = getattr(squad, unit) * \
                                                                                   getattr(squad, 'specs')[unit][
                                                                                       'damage'][
                                                                                       target_type]
            else:
                damage_dict[squad_type]['agr'] = {}
                damage_dict[squad_type]['def'] = {}

        if not 'agr' in damage_dict[squad_type]:
            damage_dict[squad_type]['agr'] = {}

        if not 'def' in damage_dict[squad_type]:
            damage_dict[squad_type]['def'] = {}

        log('damage_dict')
        log(damage_dict)

        hp_dict = {}

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

        log('hp_dict')
        log(hp_dict)

        side_damage_dict = {}
        # узнаем сколько сейчас здоровья у юнитов на поле боя
        for squad_type in squads_list:
            side_damage_dict[squad_type] = {}
            # по каждому юниту стороны боя
            static_class = ContentType.objects.get(app_label="war", model=squad_type).model_class()
            side_damage_dict[squad_type]['agr'] = {}
            side_damage_dict[squad_type]['def'] = {}
            for unit in getattr(static_class, 'specs').keys():
                # для каждого типа юнитов, по которому этот юнит может бить
                for target_type in getattr(static_class, 'specs')[unit]['damage'].keys():
                    if target_type in side_damage_dict[squad_type]['agr']:
                        side_damage_dict[squad_type]['agr'][target_type] += getattr(agr_side, unit) * \
                                                                            getattr(static_class, 'specs')[
                                                                                unit]['damage'][target_type]
                    else:
                        side_damage_dict[squad_type]['agr'][target_type] = getattr(agr_side, unit) * \
                                                                           getattr(static_class, 'specs')[
                                                                               unit]['damage'][target_type]

                    if target_type in side_damage_dict[squad_type]['def']:
                        side_damage_dict[squad_type]['def'][target_type] += getattr(def_side, unit) * \
                                                                            getattr(static_class, 'specs')[
                                                                                unit]['damage'][target_type]
                    else:
                        side_damage_dict[squad_type]['def'][target_type] = getattr(def_side, unit) * \
                                                                           getattr(static_class, 'specs')[
                                                                               unit]['damage'][target_type]

        log('side_damage_dict')
        log(side_damage_dict)

        side_hp_dict = {}
        # узнаем сколько сейчас здоровья у юнитов на поле боя
        for squad_type in squads_list:
            side_hp_dict[squad_type] = {}
            # по каждому юниту стороны боя
            static_class = ContentType.objects.get(app_label="war", model=squad_type).model_class()
            for unit in getattr(static_class, 'specs').keys():
                if 'agr' in side_hp_dict[squad_type]:
                    side_hp_dict[squad_type]['agr'] += getattr(agr_side, unit) * \
                                                       getattr(static_class, 'specs')[unit]['hp']
                else:
                    side_hp_dict[squad_type]['agr'] = getattr(agr_side, unit) * \
                                                      getattr(static_class, 'specs')[unit]['hp']

                if 'def' in side_hp_dict[squad_type]:
                    side_hp_dict[squad_type]['def'] += getattr(def_side, unit) * \
                                                       getattr(static_class, 'specs')[unit]['hp']
                else:
                    side_hp_dict[squad_type]['def'] = getattr(def_side, unit) * \
                                                      getattr(static_class, 'specs')[unit]['hp']

        log('side_hp_dict')
        log(side_hp_dict)
        # =============================================================================================================

        # юниты прошлой итерации боя получают урон от свежих юнитов текущей
        # словарь новой прочности старых отрядов. По нему будем определять потери
        new_side_hp_dict = {}
        for squad_type in squads_list:
            agr_damage = 0
            def_damage = 0
            new_side_hp_dict[squad_type] = {}
            for source_type in squads_list:
                # урон атакующему
                if 'def' in damage_dict[source_type]:
                    if squad_type in damage_dict[source_type]['def']:
                        agr_damage += damage_dict[source_type]['def'][squad_type]
                # урон обороняющемуся
                if 'agr' in damage_dict[source_type]:
                    if squad_type in damage_dict[source_type]['agr']:
                        def_damage += damage_dict[source_type]['agr'][squad_type]

            new_side_hp_dict[squad_type]['agr'] = side_hp_dict[squad_type]['agr'] - agr_damage
            new_side_hp_dict[squad_type]['def'] = side_hp_dict[squad_type]['def'] - def_damage

        # вносить урон от старой итерации по новой
        # словарь новой прочности свежих отрядов. По нему будем определять потери
        new_hp_dict = {}
        for squad_type in squads_list:
            agr_damage = 0
            def_damage = 0
            new_hp_dict[squad_type] = {}
            for source_type in squads_list:
                # урон атакующему
                if squad_type in side_damage_dict[source_type]['def']:
                    agr_damage += side_damage_dict[source_type]['def'][squad_type]
                # урон обороняющемуся
                if squad_type in side_damage_dict[source_type]['agr']:
                    def_damage += side_damage_dict[source_type]['agr'][squad_type]

            new_hp_dict[squad_type]['agr'] = hp_dict[squad_type]['agr'] - agr_damage
            new_hp_dict[squad_type]['def'] = hp_dict[squad_type]['def'] - def_damage

        # если урон остался - то свежие юниты противника получают остаток урона
        free_dmg = {}
        for squad_type in squads_list:
            free_dmg[squad_type] = {}

            if new_side_hp_dict[squad_type]['agr'] <= 0:
                # узнаем, сколько урона ещё не реализованы
                free_dmg[squad_type]['def'] = abs(new_side_hp_dict[squad_type]['agr'])
            else:
                free_dmg[squad_type]['def'] = 0

            if new_side_hp_dict[squad_type]['def'] <= 0:
                # узнаем, сколько урона ещё не реализованы
                free_dmg[squad_type]['agr'] = abs(new_side_hp_dict[squad_type]['def'])
            else:
                free_dmg[squad_type]['agr'] = 0

            # если у новых отрядов меньше прочности, чем у противника - атаки:
            if new_hp_dict[squad_type]['agr'] < free_dmg[squad_type]['def']:
                # запоминаем остаток атаки, зануляем ХП типа новых отрядов
                free_dmg[squad_type]['def'] -= new_hp_dict[squad_type]['agr']
                new_hp_dict[squad_type]['agr'] = 0
            else:
                new_hp_dict[squad_type]['agr'] = new_hp_dict[squad_type]['agr'] - free_dmg[squad_type]['def']
                free_dmg[squad_type]['def'] = 0

            if new_hp_dict[squad_type]['def'] < free_dmg[squad_type]['agr']:
                free_dmg[squad_type]['agr'] -= new_hp_dict[squad_type]['def']
                new_hp_dict[squad_type]['def'] = 0
            else:
                new_hp_dict[squad_type]['def'] = new_hp_dict[squad_type]['def'] - free_dmg[squad_type]['agr']
                free_dmg[squad_type]['agr'] = 0

        # если урон у атакующих ВСЁ ЕЩЁ остался - его получают укрепления
        agr_damage_sum = 0
        for squad_type in squads_list:
            if free_dmg[squad_type]['agr'] > 0:
                agr_damage_sum += free_dmg[squad_type]['agr']

        # ==============================================================================================================
        # считаем, сколько процентов юнитов полегло
        for squad_type in squads_list:
            static_class = ContentType.objects.get(app_label="war", model=squad_type).model_class()
            # узнаем процент выживших атаки:
            if side_hp_dict[squad_type]['agr'] == 0:
                side_lost_perc_agr = 0
            else:
                side_lost_perc_agr = new_side_hp_dict[squad_type]['agr'] / side_hp_dict[squad_type]['agr']

            # узнаем процент выживших защиты:
            if side_hp_dict[squad_type]['def'] == 0:
                side_lost_perc_def = 0
            else:
                side_lost_perc_def = new_side_hp_dict[squad_type]['def'] / side_hp_dict[squad_type]['def']

            # узнаем процент выживших новых отрядов атаки:
            if hp_dict[squad_type]['agr'] == 0:
                lost_perc_agr = 0
            else:
                lost_perc_agr = new_hp_dict[squad_type]['agr'] / hp_dict[squad_type]['agr']

            # узнаем процент выживших новых отрядов защиты:
            if hp_dict[squad_type]['def'] == 0:
                lost_perc_def = 0
            else:
                lost_perc_def = new_hp_dict[squad_type]['def'] / hp_dict[squad_type]['def']

            # по каждому юниту стороны боя
            for unit in getattr(static_class, 'specs').keys():
                if getattr(agr_side, unit) * side_lost_perc_agr < 0:
                    setattr(agr_side, unit, 0)
                else:
                    setattr(agr_side, unit, int(getattr(agr_side, unit) * side_lost_perc_agr))
                if getattr(def_side, unit) * side_lost_perc_def < 0:
                    setattr(def_side, unit, 0)
                else:
                    setattr(def_side, unit, int(getattr(def_side, unit) * side_lost_perc_def))

            # по каждому отряду типа
            for squad in squads_dict[squad_type]:
                # по каждому юниту отряда
                for unit in getattr(squad, 'specs').keys():
                    if squad.side == 'agr':
                        if getattr(squad, unit) * lost_perc_agr < 0:
                            setattr(squad, unit, 0)
                        else:
                            setattr(squad, unit, int(getattr(squad, unit) * lost_perc_agr))
                        setattr(agr_side, unit, int(getattr(agr_side, unit) + getattr(squad, unit)))
                    else:
                        if getattr(squad, unit) * lost_perc_def < 0:
                            setattr(squad, unit, 0)
                        else:
                            setattr(squad, unit, int(getattr(squad, unit) * lost_perc_def))
                        setattr(def_side, unit, int(getattr(def_side, unit) + getattr(squad, unit)))

        agr_side.save()
        def_side.save()

        if not def_side.drone and agr_side.drone > 0:
            self.recon_balance = 100
        elif not def_side.drone and not agr_side.drone:
            self.recon_balance = 1
        else:
            self.recon_balance = agr_side.drone / def_side.drone

        for squad_type in squads_list:
            squads_dict[squad_type].update(deleted=True)

        if agr_damage_sum > self.hq_points:
            self.hq_points -= agr_damage_sum
            self.war_end()
        else:
            self.hq_points -= agr_damage_sum

        if self.round == 24:
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

    def get_attrs(self):
        return {
            'hq_points': self.hq_points,
        }
