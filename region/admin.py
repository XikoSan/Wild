from django.contrib import admin

from region.building.hospital import Hospital
from region.building.power_plant import PowerPlant
from region.neighbours import Neighbours
from region.region import Region
from region.building.defences import Defences
from region.map_shape import MapShape


def recount_rating(modeladmin, request, queryset):
    queryset.model.recount_rating()


recount_rating.short_description = 'Пересчитать рейтинг'


class BuildingAdmin(admin.ModelAdmin):
    list_display = ('get_region', 'level')

    def get_region(self, obj):
        return obj.region.region_name


class RateBuildingAdmin(BuildingAdmin):
    list_display = ('get_region', 'level', 'top')
    actions = [recount_rating]

    def get_region(self, obj):
        return obj.region.region_name


class PowerPlantAdmin(BuildingAdmin):
    list_display = ('get_region', 'level')

    def get_region(self, obj):
        return obj.region.region_name


class MapShapeAdmin(admin.ModelAdmin):
    raw_id_fields = ('region',)


class RegionAdmin(admin.ModelAdmin):
    list_display = ('region_name', 'get_state', 'get_gold', 'get_oil', 'get_ore', 'is_off')

    fields = (
        # шапка
        ('is_off'),
        ('region_name', 'on_map_id'),
        # координаты
        ('is_north', 'north', 'is_east', 'east'),
        # централизация
        ('longitude', 'latitude'),
        # гос
        ('state'),
        # налоги
        ('cash_tax', 'oil_tax', 'ore_tax', 'trade_tax'),
        # ресы
        ('gold_has', 'gold_cap', 'gold_depletion'),
        ('oil_has', 'oil_cap', 'oil_depletion', 'oil_type'),
        ('ore_has', 'ore_cap', 'ore_depletion'),
        ('coal_proc', 'iron_proc', 'bauxite_proc'),
    )

    def get_state(self, obj):
        if obj.state:
            return obj.state.title
        else:
            return ''

    def get_gold(self, obj):
        return str(obj.gold_has) + '/' + str(obj.gold_cap)

    def get_oil(self, obj):
        return str(obj.oil_has) + '/' + str(obj.oil_cap) + ' (' + str(obj.oil_type) + ')'

    def get_ore(self, obj):
        return str(obj.ore_has) + '/' + str(obj.ore_cap) + ' (' + str(obj.coal_proc) + '/' + str(obj.iron_proc) + '/' + str(obj.bauxite_proc) + ')'


# Register your models here.
admin.site.register(Region, RegionAdmin)
admin.site.register(MapShape, MapShapeAdmin)
admin.site.register(Neighbours)
admin.site.register(Hospital, RateBuildingAdmin)
admin.site.register(PowerPlant, PowerPlantAdmin)
admin.site.register(Defences, BuildingAdmin)
