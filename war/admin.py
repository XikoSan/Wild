from django.contrib import admin

from war.models.wars.event_war import EventWar
from war.models.wars.ground_war import GroundWar
from war.models.wars.war_side import WarSide
from war.models.wars.unit import Unit
from war.models.wars.player_damage import PlayerDamage


class SquadAdmin(admin.ModelAdmin):
    search_fields = ['owner__nickname',]
    raw_id_fields = ('owner',)
    list_display = ['owner', 'content_type', 'object_id', 'get_agr_region', 'get_def_region', ]

    def get_agr_region(self, obj):
        war_class = obj.content_type.model_class()

        if war_class.objects.filter(pk=obj.object_id).exists():
            return str(war_class.objects.get(pk=obj.object_id).agr_region.region_name)
        else:
            return ''

    def get_def_region(self, obj):
        war_class = obj.content_type.model_class()

        if war_class.objects.filter(pk=obj.object_id).exists():
            return str(war_class.objects.get(pk=obj.object_id).def_region.region_name)
        else:
            return ''


class UnitAdmin(admin.ModelAdmin):
    search_fields = ['good__name_ru',]
    raw_id_fields = ('good',)
    list_display = ['get_unit_name', 'damage', 'energy', ]

    def get_unit_name(self, obj):
        return obj.good.name


# Register your models here.
admin.site.register(EventWar)
admin.site.register(GroundWar)
admin.site.register(WarSide)

admin.site.register(PlayerDamage)
admin.site.register(Unit, UnitAdmin)
