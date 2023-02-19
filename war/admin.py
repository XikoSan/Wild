from django.contrib import admin

from war.models.squads.heavy_vehicle import HeavyVehicle
from war.models.squads.recon import Recon
from war.models.squads.infantry import Infantry
from war.models.squads.light_vehicle import LightVehicle
from war.models.wars.event_war import EventWar
from war.models.wars.ground_war import GroundWar
from war.models.wars.war_side import WarSide


class SquadAdmin(admin.ModelAdmin):
    search_fields = ['owner__nickname',]
    raw_id_fields = ('owner',)
    list_display = ['owner', 'content_type', 'object_id', 'get_agr_region', 'get_def_region', ]

    def get_agr_region(self, obj):
        war_class = obj.content_type.model_class()

        if war_class.objects.filter(pk=obj.object_id).exists():
            return str(workplace_class.objects.get(pk=obj.object_id).agr_region.region_name)
        else:
            return ''

    def get_def_region(self, obj):
        war_class = obj.content_type.model_class()

        if war_class.objects.filter(pk=obj.object_id).exists():
            return str(workplace_class.objects.get(pk=obj.object_id).def_region.region_name)
        else:
            return ''

# Register your models here.
admin.site.register(EventWar)
admin.site.register(GroundWar)
admin.site.register(WarSide)

admin.site.register(Recon, SquadAdmin)
admin.site.register(Infantry, SquadAdmin)
admin.site.register(LightVehicle, SquadAdmin)
admin.site.register(HeavyVehicle, SquadAdmin)
