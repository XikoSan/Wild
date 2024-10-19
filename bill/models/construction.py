# coding=utf-8

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy, pgettext
from region.building.building import Building
from region.models.region import Region
from bill.models.bill import Bill
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.treasury import Treasury
from storage.models.storage import Storage
from player.views.get_subclasses import get_subclasses
from region.building.rate_building import RateBuilding
from state.models.treasury_stock import TreasuryStock
from storage.models.good import Good
import copy
from django.db.models import F
from war.models.martial import Martial
from django.utils.translation import pgettext_lazy


# Построить здание
class Construction(Bill):
    # -------------vvvvvvv---------------Строительные схемы---------------vvvvvvv---------------
    Hospital = {
        'title': pgettext_lazy('new_bill', "Больница"),

        'resources':
            {
                'Наличные': 800,
                'Медикаменты': 15,
            },
    }

    PowerPlant = {
        'title': pgettext_lazy('new_bill', "ТЭЦ"),

        'resources':
            {
                'Наличные': 100,
                'Сталь': 50,
                'Уголь': 100,
            },
    }

    Defences = {
        'title': pgettext_lazy('new_bill', "Укрепления"),

        'resources':
            {
                'Наличные': 500,
                'Сталь': 90,
            },
    }

    Infrastructure = {
        'title': pgettext_lazy('new_bill', "Инфраструктура"),

        'resources':
            {
                'Наличные': 500,
                'Алюминий': 50,
            },
    }

    # регион разведки
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион строительства')

    # получим классы всех строений
    building_classes = get_subclasses(Building)
    # строение
    building_schemas = ()

    for building_cl in building_classes:
        building_schemas = building_schemas + ((building_cl.__name__, building_cl._meta.verbose_name),)

    building = models.CharField(
        max_length=20,
        choices=building_schemas,
        blank=True,
        null=True,
        default=None,
        verbose_name='Здание',
    )
    # объем строительства
    exp_value = models.IntegerField(default=1, verbose_name='Объем строительства')

    @staticmethod
    def new_bill(request, player, parliament):

        if Construction.objects.filter(running=True, initiator=player).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Ограничение: не более одного законопроекта данного типа'),
            }

        try:
            construction_region = int(request.POST.get('construction_regions'))

        except ValueError:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'ID региона должен быть целым числом'),
            }

        if Region.objects.filter(pk=construction_region, state=parliament.state).exists():

            region = Region.objects.get(pk=construction_region, state=parliament.state)

            if Martial.objects.filter(active=True, state=parliament.state, region=region).exists():
                return {
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                    'response': pgettext('new_bill', 'В данном регионе введено военное положение'),
                }

            schemas_list = []
            for schema in Construction.building_schemas:
                schemas_list.append(schema[0])

            building = request.POST.get('construction_buildings')

            if building in schemas_list:

                try:
                    new_levels = int(request.POST.get('construction_value'))

                except ValueError:
                    return {
                        'header': pgettext('new_bill', 'Новый законопроект'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                        'response': pgettext('new_bill', 'Уровни здания должны быть целым числом'),
                    }

                if not 1 <= new_levels <= 1000:
                    return {
                        'header': pgettext('new_bill', 'Новый законопроект'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                        'response': pgettext('new_bill', 'Уровни здания должны быть числом в интервале 1-1000'),
                    }

                # ура, все проверили
                bill = Construction(
                    running=True,
                    parliament=parliament,
                    initiator=player,
                    voting_start=timezone.now(),

                    region=region,
                    building=building,
                    exp_value=new_levels,
                )
                bill.save()

                return {
                    'response': 'ok',
                }

            else:
                return {
                    'response': pgettext('new_bill', 'Нет такого здания'),
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
        else:
            return {
                'response': pgettext('new_bill', 'Нет такого региона'),
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }

    # выполнить законопроект
    def do_bill(self):
        b_type = None
        building = None
        treasury = Treasury.get_instance(state=self.parliament.state)

        # получим классы всех строений
        building_classes = get_subclasses(Building)

        building_dict = {}

        for building_cl in building_classes:
            building_dict[building_cl.__name__] = building_cl

        #  если введено военное положение
        if Martial.objects.filter(active=True, state=self.parliament.state, region=self.region).exists():
            b_type = 'rj'

        else:

            if self.region.state == self.parliament.state:
                # если такой тип строений существует
                if self.building in building_dict:

                    if treasury.cash != 0:

                        if self.building:

                            if building_dict[self.building].objects.filter(region=self.region).exists():
                                building = building_dict[self.building].objects.get(region=self.region)

                            else:
                                # создание строения в указанном регионе
                                building = building_dict[self.building](region=self.region)

                            # проверяем наличие всех ресурсов в казне, для стройки
                            all_exists = True

                            # todo: перенести словари компонентов, требуемых для постройки, в классы зданий
                            for component in getattr(self, self.building)['resources'].keys():

                                exp_price = getattr(self, self.building)['resources'][component] * self.exp_value

                                if component == 'Наличные':
                                    if getattr(treasury, 'cash') < exp_price:
                                        all_exists = False
                                        break

                                elif not TreasuryStock.objects.filter(treasury=treasury,
                                                                          good=Good.objects.get(name=component),
                                                                          stock__gte=exp_price
                                                                      ).exists():
                                    all_exists = False
                                    break

                            if all_exists:
                                setattr(building, 'level', getattr(building, 'level') + self.exp_value)

                                for resource in getattr(self, self.building)['resources'].keys():

                                    exp_price = getattr(self, self.building)['resources'][resource] * self.exp_value

                                    if resource == 'Наличные':
                                        treasury.cash -= exp_price

                                    else:
                                        TreasuryStock.objects.filter(treasury=treasury,
                                                                     good=Good.objects.get(name=resource),
                                                                     stock__gte=exp_price
                                                                     ).update(stock=F('stock') - exp_price)

                                b_type = 'ac'

                            else:
                                b_type = 'rj'
                        else:
                            b_type = 'rj'

                        # если закон принят
                        if b_type == 'ac':
                            self.save()
                            treasury.save()
                            building.save()

                            # если это рейтинговое строение
                            if RateBuilding in building_dict[self.building].__bases__:
                                # пересчитаем рейтинг
                                building_dict[self.building].recount_rating()

                            elif self.building == 'PowerPlant':
                                for building_cl in building_classes:
                                    if RateBuilding in building_cl.__bases__:
                                        # пересчитаем рейтинг
                                        building_cl.recount_rating()

                    else:
                        b_type = 'rj'
                else:
                    b_type = 'rj'
            else:
                b_type = 'rj'

        Construction.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):

        regions = Region.objects.filter(state=state)

        # получим классы всех строений
        building_classes = get_subclasses(Building)

        building_dict = {}

        for building_cl in building_classes:
            building_dict[building_cl.__name__] = {}

            buildings = building_cl.objects.filter(region__in=regions)

            for region in regions:
                if buildings.filter(region=region).exists():
                    building_dict[building_cl.__name__][region.pk] = buildings.get(region=region).level
                else:
                    building_dict[building_cl.__name__][region.pk] = 0

        material_dict = {}

        build_dict = {}
        for schema in Construction.building_schemas:

            schema_ins = copy.deepcopy(getattr(Construction, schema[0]))

            resources = {}

            for resource in schema_ins['resources'].keys():

                if resource == 'Наличные':
                    resources[0] = schema_ins['resources'][resource]

                else:
                    if resource not in material_dict:
                        material = Good.objects.get(name_ru=resource)
                        material_dict[resource] = material

                    else:
                        material = material_dict[resource]

                    resources[material.pk] = schema_ins['resources'][resource]

            schema_ins['resources'] = resources

            build_dict[schema[0]] = schema_ins

        good_names = {}

        for good_key in material_dict.keys():
            good_names[material_dict[good_key].pk] = material_dict[good_key].name

        good_names[0] = pgettext('goods', 'Наличные')

        data = {
            'regions': regions,
            'schemas': build_dict,
            'buildings': building_dict,
            'good_names': good_names,
            'crude_list': ['valut', 'minerals', 'oils', 'materials', 'equipments'],
        }

        return data, 'state/gov/drafts/construction.html'

    @staticmethod
    def get_new_draft(state):

        martial_regions = Martial.objects.filter(active=True, state=state).values_list('region__pk')
        mar_pk_list = []

        for m_reg in martial_regions:
            mar_pk_list.append(m_reg[0])

        regions = Region.objects.filter(state=state).exclude(pk__in=mar_pk_list)

        # получим классы всех строений
        building_classes = get_subclasses(Building)

        building_dict = {}

        for building_cl in building_classes:
            building_dict[building_cl.__name__] = {}

            buildings = building_cl.objects.filter(region__in=regions)

            for region in regions:
                if buildings.filter(region=region).exists():
                    building_dict[building_cl.__name__][region.pk] = buildings.get(region=region).level
                else:
                    building_dict[building_cl.__name__][region.pk] = 0

        material_dict = {}

        build_dict = {}
        for schema in Construction.building_schemas:

            schema_ins = copy.deepcopy(getattr(Construction, schema[0]))

            resources = {}

            for resource in schema_ins['resources'].keys():

                if resource == 'Наличные':
                    resources[0] = schema_ins['resources'][resource]

                else:
                    if resource not in material_dict:
                        material = Good.objects.get(name_ru=resource)
                        material_dict[resource] = material

                    else:
                        material = material_dict[resource]

                    resources[material.pk] = schema_ins['resources'][resource]

            schema_ins['resources'] = resources

            build_dict[schema[0]] = schema_ins

        good_names = {}

        for good_key in material_dict.keys():
            good_names[material_dict[good_key].pk] = material_dict[good_key].name

        good_names[0] = pgettext('goods', 'Наличные')

        data = {
            'regions': regions,
            'schemas': build_dict,
            'buildings': building_dict,
            'good_names': good_names,
            'crude_list': ['valut', 'minerals', 'oils', 'materials', 'equipments'],
        }

        return data, 'state/redesign/drafts/construction.html'

    def get_bill(self, player, minister, president):

        resources = getattr(self, self.building)['resources'].keys()

        goods = Good.objects.filter(name_ru__in=resources, type__in=['minerals', 'oils', 'materials', 'equipments'])

        good_names = {}
        for resource in resources:
            if resource == 'Наличные':
                good_names['Наличные'] = pgettext('goods', 'Наличные')
            else:
                good_names[resource] = goods.get(name_ru=resource).name

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
            'good_names': good_names
        }

        return data, 'state/gov/bills/construction.html'

    def get_new_bill(self, player, minister, president):

        resources = getattr(self, self.building)['resources'].keys()

        goods = Good.objects.filter(name_ru__in=resources, type__in=['minerals', 'oils', 'materials', 'equipments'])

        good_names = {}
        for resource in resources:
            if resource == 'Наличные':
                good_names['Наличные'] = pgettext('goods', 'Наличные')
            else:
                good_names[resource] = goods.get(name_ru=resource).name

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
            'good_names': good_names
        }

        return data, 'state/redesign/bills/construction.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        resources = getattr(self, self.building)['resources'].keys()

        goods = Good.objects.filter(name_ru__in=resources, type__in=['minerals', 'oils', 'materials', 'equipments'])

        good_names = {}
        for resource in resources:
            if resource == 'Наличные':
                good_names['Наличные'] = pgettext('goods', 'Наличные')
            else:
                good_names[resource] = goods.get(name_ru=resource).name

        data = {'bill': self,
                'title': self._meta.verbose_name_raw,
                'player': player,
                'good_names': good_names}

        return data, 'state/gov/reviewed/construction.html'

# получить шаблон рассмотренного законопроекта
    def get_new_reviewed_bill(self, player):

        resources = getattr(self, self.building)['resources'].keys()

        goods = Good.objects.filter(name_ru__in=resources, type__in=['minerals', 'oils', 'materials', 'equipments'])

        good_names = {}
        for resource in resources:
            if resource == 'Наличные':
                good_names['Наличные'] = pgettext('goods', 'Наличные')
            else:
                good_names[resource] = goods.get(name_ru=resource).name

        data = {'bill': self,
                'title': self._meta.verbose_name_raw,
                'player': player,
                'good_names': good_names}

        return data, 'state/redesign/reviewed/construction.html'

    def __str__(self):
        return str(self.exp_value) + " " + self.get_building_display() + " в " + self.region.region_name

    # Свойства класса
    class Meta:

        verbose_name = pgettext_lazy('new_bill', "Строительство")
        verbose_name_plural = pgettext_lazy('new_bill', "Строительства")


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=Construction)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=Construction)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()