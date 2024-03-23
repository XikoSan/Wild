from django.contrib import admin

from event.models.enter_event.activity_event import ActivityEvent
from event.models.enter_event.event_part import ActivityEventPart
from event.models.enter_event.global_part import ActivityGlobalPart

from event.models.inviting_event.cash_event import CashEvent
from event.models.inviting_event.invite import Invite


class EventPartAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname', ]
    raw_id_fields = ('player', 'event')


class GlobalPartAdmin(admin.ModelAdmin):
    raw_id_fields = ('event',)


class InviteAdmin(admin.ModelAdmin):
    list_display = ('sender', 'invited')
    search_fields = ['sender__nickname', 'invited__nickname', ]
    raw_id_fields = ('sender', 'invited')


# Register your models here.
admin.site.register(ActivityEvent)
admin.site.register(ActivityEventPart, EventPartAdmin)
admin.site.register(ActivityGlobalPart, GlobalPartAdmin)

admin.site.register(CashEvent)
admin.site.register(Invite, InviteAdmin)
