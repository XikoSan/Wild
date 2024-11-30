from django.contrib import admin

from party.logs.membership_log import MembershipLog
from party.logs.party_apply import PartyApply
from party.logs.party_gold_log import PartyGoldLog
from party.party import Party
from party.position import PartyPosition
from party.primaries.primaries import Primaries
from party.primaries.primaries_bulletin import PrimBulletin
from party.primaries.primaries_leader import PrimariesLeader


class PartyAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'region', 'deleted')

    fields = (
        # шапка
        ('title', 'region', 'deleted'),
        #
        ('foundation_date', 'get_primaries_day'),
        #
        ('image', 'members_image'),
        #
        ('gold', 'description'),
        #
        ('task'),
    )

    def get_primaries_day(self, obj):
        days_dict = {
            0: "понедельник",
            1: "вторник",
            2: "среда",
            3: "четверг",
            4: "пятница",
            5: "суббота",
            6: "воскресенье",
        }
        return f'{obj.primaries_day} ({days_dict[obj.primaries_day]})'

    get_primaries_day.short_description = 'День недели'

    readonly_fields = ('get_primaries_day',)


class PrimariesAdmin(admin.ModelAdmin):
    search_fields = ['party__title', ]


class PartyGoldLogAdmin(admin.ModelAdmin):
    search_fields = ['party__title', ]
    list_display = ('dtime', 'party', 'gold', 'activity_txt',)
    raw_id_fields = ('party',)
    list_filter = ('activity_txt',)
    date_hierarchy = 'dtime'
    ordering = ('-dtime',)


# Register your models here.
admin.site.register(Party, PartyAdmin)
admin.site.register(PartyPosition)
admin.site.register(Primaries, PrimariesAdmin)
admin.site.register(PrimBulletin)
admin.site.register(PrimariesLeader)
admin.site.register(PartyApply)
admin.site.register(MembershipLog)
admin.site.register(PartyGoldLog, PartyGoldLogAdmin)
