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
from django.db.models.signals import post_delete
from django.dispatch import receiver
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
                      'agr':{},
                      'def':{}
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

                            if target_type in damage_dict[squad.side]:
                                damage_dict[squad.side][target_type] += getattr(squad, unit) * \
                                                                                    getattr(squad, 'specs')[unit][
                                                                                        'damage'][
                                                                                        target_type]
                            else:
                                damage_dict[squad.side][target_type] = getattr(squad, unit) * \
                                                                                   getattr(squad, 'specs')[unit][
                                                                                       'damage'][
                                                                                       target_type]
                            # vvvvvvvvvv логи vvvvvvvvvv
                            if self.squads_dict[target_type] in types_damage_dict[squad.side]:
                                types_damage_dict[squad.side][self.squads_dict[target_type]] += getattr(squad, unit) * \
                                                                                    getattr(squad, 'specs')[unit][
                                                                                        'damage'][
                                                                                        target_type]
                            else:
                                types_damage_dict[squad.side][self.squads_dict[target_type]] = getattr(squad, unit) * \
                                                                                    getattr(squad, 'specs')[unit][
                                                                                        'damage'][
                                                                                        target_type]
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
                                hp_log_dict[squad.side][self.squads_dict[squad_type]] += getattr(squad, unit) * getattr(squad, 'specs')[unit][
                                    'hp']
                            else:
                                hp_log_dict[squad.side][self.squads_dict[squad_type]] = getattr(squad, unit) * getattr(squad, 'specs')[unit][
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
                lost_per_log_dict['agr'][self.squads_dict[squad_type]] = int(new_hp_dict[squad_type]['agr'] / hp_dict[squad_type]['agr'] * 100)

            # узнаем процент выживших новых отрядов защиты:
            if hp_dict[squad_type]['def'] == 0:
                lost_perc_def = 0
                lost_per_log_dict['def'][self.squads_dict[squad_type]] = 0
            else:
                lost_perc_def = new_hp_dict[squad_type]['def'] / hp_dict[squad_type]['def']
                lost_per_log_dict['def'][self.squads_dict[squad_type]] = int(new_hp_dict[squad_type]['def'] / hp_dict[squad_type]['def'] * 100)

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
            self.round_log += '<div class="row" align="center" style="margin-top: 10px">' + str(agr_damage_sum) + '</div>'
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


# сигнал прослушивающий создание партии, после этого формирующий таску
@receiver(post_delete, sender=EventWar)
def delete_post(sender, instance, **kwargs):

    instance.task.delete()

