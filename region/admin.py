from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models
from django.utils.html import format_html

from region.building.defences import Defences
from region.building.hospital import Hospital
from region.building.infrastructure import Infrastructure
from region.building.power_plant import PowerPlant
from region.models.fossils import Fossils
from region.models.map_shape import MapShape
from region.models.neighbours import Neighbours
from region.models.plane import Plane
from region.models.region import Region
from region.models.terrain.terrain import Terrain
from region.models.terrain.terrain_modifier import TerrainModifier
from modeltranslation.admin import TabbedTranslationAdmin


def recount_rating(modeladmin, request, queryset):
    queryset.model.recount_rating()


recount_rating.short_description = 'Пересчитать рейтинг'


class BuildingAdmin(admin.ModelAdmin):
    list_display = ('get_region', 'level')

    def get_region(self, obj):
        return obj.region.region_name


class PlaneAdmin(admin.ModelAdmin):
    list_display = ('plane', 'player')

    raw_id_fields = ('player',)

    fields = ['in_use', 'player', 'plane', 'color', 'nickname', 'number', 'image_tag']
    readonly_fields = ['image_tag', 'number']


class FossilsAdmin(admin.ModelAdmin):
    search_fields = ['region__region_name', 'good__name']
    list_filter = ('good',)
    raw_id_fields = ('region', 'good',)
    list_display = ('get_region', 'get_good', 'percent')

    def get_region(self, obj):

        if self.region.region_name:
            reg_name = self.region.region_name
        else:
            reg_name = self.region.region_name_ru

        return reg_name

    def get_good(self, obj):
        return obj.good.name


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


class TerrainModifierAdmin(admin.ModelAdmin):
    list_display = ('terrain', 'unit', 'modifier')

    raw_id_fields = ('terrain', 'unit',)


class TerrainModifierInline(admin.TabularInline):
    model = TerrainModifier


class TerrainAdmin(admin.ModelAdmin):
    inlines = [TerrainModifierInline]


class FossilsInline(admin.TabularInline):
    model = Fossils


class RegionAdmin(TabbedTranslationAdmin):
    search_fields = ['state__title', 'region_name', 'on_map_id']

    list_tabs = ['region_name', ]
    list_display = ('region_name', 'get_state', 'get_gold', 'get_oil', 'get_ore', 'is_off')

    inlines = [FossilsInline]

    fields = (
        # шапка
        ('region_name'),
        ('on_map_id'),
        ('is_off', 'limit_id'),
        # координаты
        ('is_north', 'north', 'is_east', 'east'),
        # централизация
        ('longitude', 'latitude'),
        # гос
        ('state', 'joined_since', 'peace_date'),
        # налоги
        ('cash_tax', 'oil_tax', 'ore_tax', 'trade_tax'),
        # ресы
        ('gold_has', 'gold_cap', 'gold_depletion'),
        ('oil_has', 'oil_cap', 'oil_depletion', 'oil_type', 'oil_mark'),
        ('ore_has', 'ore_cap', 'ore_depletion'),
        ('coal_proc', 'iron_proc', 'bauxite_proc'),
        ('terrain'),
    )

    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.FilteredSelectMultiple(
            verbose_name='Рельеф',
            is_stacked=False
        )},
    }

    # def get_region_name(self, obj):
    #     if obj.state:
    #         return obj.state.title
    #     else:
    #         return ''

    def get_state(self, obj):
        if obj.state:
            return obj.state.title
        else:
            return ''

    def get_gold(self, obj):
        return str(obj.gold_has) + '/' + str(obj.gold_cap)

    def get_oil(self, obj):
        return str(obj.oil_has) + '/' + str(obj.oil_cap) + ' (' + str(obj.oil_mark.name) + ')'

    def get_ore(self, obj):
        return str(obj.ore_has) + '/' + str(obj.ore_cap) + ' (' + str(obj.coal_proc) + '/' + str(
            obj.iron_proc) + '/' + str(obj.bauxite_proc) + ')'


# Register your models here.
admin.site.register(Region, RegionAdmin)
admin.site.register(MapShape, MapShapeAdmin)
admin.site.register(Neighbours)
admin.site.register(Fossils, FossilsAdmin)
admin.site.register(Hospital, RateBuildingAdmin)
admin.site.register(Infrastructure, RateBuildingAdmin)
admin.site.register(PowerPlant, PowerPlantAdmin)
admin.site.register(Defences, BuildingAdmin)
admin.site.register(Terrain, TerrainAdmin)
admin.site.register(TerrainModifier, TerrainModifierAdmin)

admin.site.register(Plane, PlaneAdmin)
