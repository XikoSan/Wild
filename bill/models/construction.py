# coding=utf-8

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy
from region.building.building import Building
from region.region import Region
from bill.models.bill import Bill
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.treasury import Treasury
from storage.models.storage import Storage
from player.views.get_subclasses import get_subclasses
from region.building.rate_building import RateBuilding

# Построить здание
class Construction(Bill):
    # -------------vvvvvvv---------------Строительные схемы---------------vvvvvvv---------------
    Hospital = {
        'title': 'Больницы',

        'resources':
            {
                'cash': 800,
                'medical': 15,
            },
    }

    PowerPlant = {
        'title': 'ТЭЦ',

        'resources':
            {
                'cash': 100,
                'steel': 50,
                'coal': 100,
            },
    }

    Defences = {
        'title': 'Укрепления',

        'resources':
            {
                'cash': 1000,
                'steel': 100,
                'coal': 50,
            },
    }

    # регион разведки
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион строительства')

    # получим классы всех строений
    building_classes = get_subclasses(Building)
    # строение
    building_schemas = ()

    for building_cl in building_classes:
        building_schemas = building_schemas + ((building_cl.__name__, building_cl._meta.verbose_name_raw),)

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
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Ограничение: не более одного законопроекта данного типа',
            }

        try:
            construction_region = int(request.POST.get('construction_regions'))

        except ValueError:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'ID региона должен быть целым числом',
            }

        if Region.objects.filter(pk=construction_region, state=parliament.state).exists():

            region = Region.objects.get(pk=construction_region, state=parliament.state)

            schemas_list = []
            for schema in Construction.building_schemas:
                schemas_list.append(schema[0])

            building = request.POST.get('construction_buildings')

            if building in schemas_list:

                try:
                    new_levels = int(request.POST.get('construction_value'))

                except ValueError:
                    return {
                        'header': 'Новый законопроект',
                        'grey_btn': 'Закрыть',
                        'response': 'Уровни здания должны быть целым числом',
                    }

                if not 1 <= new_levels <= 1000:
                    return {
                        'header': 'Новый законопроект',
                        'grey_btn': 'Закрыть',
                        'response': 'Уровни здания должны быть числом в интервале 1-1000',
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
                    'response': 'Нет такого здания',
                    'header': 'Новый законопроект',
                    'grey_btn': 'Закрыть',
                }
        else:
            return {
                'response': 'Нет такого региона',
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
            }

    # выполнить законопроект
    def do_bill(self):
        b_type = None
        treasury = Treasury.get_instance(state=self.parliament.state)

        # получим классы всех строений
        building_classes = get_subclasses(Building)

        building_dict = {}

        for building_cl in building_classes:
            building_dict[building_cl.__name__] = building_cl

        # если такой тип строений существует
        if self.building in building_dict:

            if treasury.cash != 0:

                if self.building:

                    if building_dict[self.building].objects.filter(region=self.region).exists():
                        building = building_dict[self.building].objects.get(region=self.region)

                    else:
                        building = building_dict[self.building](region=self.region)

                    # проверяем наличие всех ресурсов в казне, для стройки
                    all_exists = True

                    for component in getattr(self, self.building)['resources'].keys():
                        if getattr(treasury, component) < getattr(self, self.building)['resources'][component] * self.exp_value:
                            all_exists = False
                            break

                    if all_exists:
                        setattr(building, 'level', getattr(building, 'level') + self.exp_value)

                        for resource in getattr(self, self.building)['resources'].keys():
                            setattr(treasury, resource,
                                    getattr(treasury, resource) - (
                                                getattr(self, self.building)['resources'][resource] * self.exp_value))

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

        build_dict = {}
        for schema in Construction.building_schemas:
            build_dict[schema[0]] = getattr(Construction, schema[0])

        data = {
            'regions': regions,
            'schemas': build_dict,
            'buildings': building_dict,
            'storage_cl': Storage,
            'crude_list': ['valut', 'minerals', 'oils', 'materials', 'equipments'],
        }

        return data, 'state/gov/drafts/construction.html'

    def get_bill(self, player, minister, president):

        good_names = {}
        for crude in ['valut', 'minerals', 'oils', 'materials', 'equipments']:
            for good in getattr(Storage, crude):
                good_names[good] = getattr(Storage, crude)[good]

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

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        good_names = {}
        for crude in ['valut', 'minerals', 'oils', 'materials', 'equipments']:
            for good in getattr(Storage, crude):
                good_names[good] = getattr(Storage, crude)[good]

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player, 'good_names': good_names}

        return data, 'state/gov/reviewed/construction.html'

    def __str__(self):
        return str(self.exp_value) + " " + self.get_building_display() + " в " + self.region.region_name

    # Свойства класса
    class Meta:

        verbose_name = "Строительство"
        verbose_name_plural = "Строительства"


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