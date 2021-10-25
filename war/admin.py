from django.contrib import admin

from war.models.squads.infantry import Infantry
from war.models.wars.event_war import EventWar
from war.models.wars.war_side import WarSide

# Register your models here.
admin.site.register(EventWar)
admin.site.register(Infantry)
admin.site.register(WarSide)
