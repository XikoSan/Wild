# coding=utf-8

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import pgettext
from bill.models.bill import Bill
from bill.views.get_victim_regions import get_victims
from player.views.get_subclasses import get_subclasses
from region.models.neighbours import Neighbours
from region.models.region import Region
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from war.models.wars.war import War
from war.models.wars.event_war import EventWar
from war.models.wars.ground_war import GroundWar


# Объявить войну
class StartWar(Bill):
    # возможность принять закон досрочно
    accept_ahead = False

    # получим классы всех войн
    war_classes = get_subclasses(War)
    # строение
    war_choices = ()

    for war_cl in war_classes:
        if war_cl.__name__ == 'EventWar':
            continue
        war_choices = war_choices + ((war_cl.__name__, war_cl._meta.verbose_name_raw),)

    war_type = models.CharField(
        max_length=20,
        choices=war_choices,
        blank=True,
        null=True,
        default=None,
        verbose_name='Тип войны',
    )

    # регион атаки
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион-плацдарм',
                               related_name="region_from")
    # регион атаки
    region_to = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион-цель',
                                  related_name="region_to")

    def check_ahead(self):

        if not self.region_to.state:
            return self.accept_ahead

        # получим классы всех войн
        war_classes = get_subclasses(War)

        agr_regions = Region.objects.filter(state=self.parliament.state)
        def_regions = Region.objects.filter(state=self.region_to.state)

        accept_ahead = self.accept_ahead

        # проверяем по всем классам войн. Если есть атака - можно ускорить
        for war_class in war_classes:
            if war_class.objects.filter(
                                        running=True,
                                        agr_region__in=def_regions,
                                        def_region__in=agr_regions,
                                        deleted=False
                                ).exists():
                accept_ahead = True
                break

        return accept_ahead


    @staticmethod
    def new_bill(request, player, parliament):

        if StartWar.objects.filter(running=True, initiator=player).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Ограничение: не более одного законопроекта данного типа'),
            }
        # если айди корректное
        try:
            region_from = int(request.POST.get('war_region_from'))

        except ValueError:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'ID плацдарма должен быть целым числом'),
            }

        if not Region.objects.filter(pk=region_from).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Неизвестный плацдарм'),
            }
        # если айди корректное
        try:
            region_to = int(request.POST.get('war_region_to'))

        except ValueError:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'ID целевого региона должен быть целым числом'),
            }

        if not Region.objects.filter(pk=region_to).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Неизвестный целевой регион'),
            }
        # регион не один и тот же
        if region_to == region_from:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Нельзя напасть на самих себя'),
            }

        region_from = Region.objects.get(pk=region_from)

        region_to = Region.objects.get(pk=region_to)
        # гос регионов не один и тот же
        if region_to.state == region_from.state:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Нельзя напасть на самих себя'),
            }

        # получим классы всех войн
        war_classes = get_subclasses(War)
        class_ok = False
        war_class = None

        for war_cl in war_classes:
            # if war_cl.__name__ == request.POST.get('war_war_type'):
            if war_cl.__name__ == 'GroundWar':
                class_ok = True
                war_class = war_cl
                break

        if not class_ok:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Такого вида войн не существует'),
            }

        if war_class.objects.filter(
                running=True,
                agr_region=region_from,
                def_region=region_to,
                deleted=False
        ).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Такая война уже идёт'),
            }

        # если связь регионов есть
        if not Neighbours.objects.filter(Q(region_1=region_from,
                                           region_2=region_to) | Q(
            region_1=region_to,
            region_2=region_from)).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Указанные регионы не граничат между собой'),
            }

        # ура, все проверили
        bill = StartWar(
            running=True,
            parliament=parliament,
            initiator=player,
            voting_start=timezone.now(),

            # war_type=request.POST.get('war_war_type'),
            war_type='GroundWar',
            region=region_from,
            region_to=region_to
        )
        bill.save()

        return {
            'response': 'ok',
        }

    # выполнить законопроект
    def do_bill(self):
        b_type = None

        if self.region.state == self.parliament.state:

            if self.region_to.peace_date > timezone.now():
                b_type = 'rj'

            else:
                # получим классы всех войн
                war_classes = get_subclasses(War)
                war_class = None

                for war_cl in war_classes:
                    if war_cl.__name__ == self.war_type:
                        war_class = war_cl
                        break

                if war_class.objects.filter(
                        running=True,
                        agr_region=self.region,
                        def_region=self.region_to,
                        deleted=False
                ).exists():
                    b_type = 'rj'

                else:
                    b_type = 'ac'

                # если закон принят
                if b_type == 'ac':
                    new_war = war_class(
                        running=True,
                        agr_region=self.region,
                        def_region=self.region_to,
                    )

                    new_war.save()
        else:
            b_type = 'rj'

        StartWar.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):

        first = None
        victimRegions = get_victims(state)

        if len(list(victimRegions.keys())) > 0:
            first = list(victimRegions.keys())[0]

        data = {
            'reg_list': list(victimRegions.keys()),
            'first': first,
            'victims_list': victimRegions,
        }

        return data, 'state/gov/drafts/start_war.html'

    @staticmethod
    def get_new_draft(state):

        first = None
        victimRegions = get_victims(state)

        if len(list(victimRegions.keys())) > 0:
            first = list(victimRegions.keys())[0]

        data = {
            'reg_list': list(victimRegions.keys()),
            'first': first,
            'victims_list': victimRegions,
        }

        return data, 'state/redesign/drafts/start_war.html'

    def get_bill(self, player, minister, president):

        has_right = False
        if minister:
            for right in minister.rights.all():
                if self.__class__.__name__ == right.right:
                    has_right = True
                    break

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            'president': president,
            'has_right': has_right,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/gov/bills/start_war.html'

    def get_new_bill(self, player, minister, president):

        has_right = False
        if minister:
            for right in minister.rights.all():
                if self.__class__.__name__ == right.right:
                    has_right = True
                    break

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            'president': president,
            'has_right': has_right,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/redesign/bills/start_war.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/gov/reviewed/start_war.html'

    # получить шаблон рассмотренного законопроекта
    def get_new_reviewed_bill(self, player):
        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/redesign/reviewed/start_war.html'

    def __str__(self):
        return self.region.region_name + ' против ' + self.region_to.region_name

    # Свойства класса
    class Meta:
        # abstract = True
        verbose_name = "Объявление войны"
        verbose_name_plural = "Объявления войн"


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=StartWar)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=StartWar)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
