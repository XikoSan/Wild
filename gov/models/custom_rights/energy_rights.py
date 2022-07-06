from gov.models.custom_rights.custom_right import CustomRight
from region.building.power_plant import PowerPlant
from region.region import Region
from storage.models.storage import Storage
from player.views.get_subclasses import get_subclasses
from bill.models.construction import Construction


# кастомное право министра энергетики
class EnergyRights(CustomRight):

    # получить шаблон прав министра
    @staticmethod
    def get_form(state):
        regions = Region.objects.filter(state=state)

        building_dict = {}
        building_fact_dict = {}

        buildings = PowerPlant.objects.filter(region__in=regions)

        for region in regions:
            if buildings.filter(region=region).exists():
                building_dict[region.pk] = buildings.get(region=region).level
                if buildings.get(region=region).level_on:
                    building_fact_dict[region.pk] = buildings.get(region=region).level_on
            else:
                building_dict[region.pk] = 0

        data = {
            'regions': regions,
            'buildings': building_dict,
            'buildings_fact': building_fact_dict,
        }

        return data, 'state/gov/forms/energy_right.html'

    # Свойства класса
    class Meta:
        abstract = True
        verbose_name = "Министр энергетики"
        verbose_name_plural = "Министр энергетики"
