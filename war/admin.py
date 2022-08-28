from django.contrib import admin

from war.models.squads.heavy_vehicle import HeavyVehicle
from war.models.squads.recon import Recon
from war.models.squads.infantry import Infantry
from war.models.squads.light_vehicle import LightVehicle
from war.models.wars.event_war import EventWar
from war.models.wars.war_side import WarSide

# Register your models here.
admin.site.register(EventWar)
admin.site.register(Recon)
admin.site.register(Infantry)
admin.site.register(LightVehicle)
admin.site.register(HeavyVehicle)
admin.site.register(WarSide)
