from django.contrib import admin

from event.models.enter_event.activity_event import ActivityEvent
from event.models.enter_event.event_part import ActivityEventPart
from event.models.enter_event.global_part import ActivityGlobalPart


class EventPartAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname', ]
    raw_id_fields = ('player', 'event')


class GlobalPartAdmin(admin.ModelAdmin):
    raw_id_fields = ('event',)


# Register your models here.
admin.site.register(ActivityEvent)
admin.site.register(ActivityEventPart, EventPartAdmin)
admin.site.register(ActivityGlobalPart, GlobalPartAdmin)
