from django.contrib import admin

from player.logs.cash_log import CashLog
from .player import Player


class CashLogAdmin(admin.ModelAdmin):
    list_display = ('player', 'cash', 'activity_txt')
    list_filter = ('activity_txt',)
    search_fields = ('player',)
    raw_id_fields = ('player',)
    date_hierarchy = 'dtime'
    ordering = ('-dtime',)


# Register your models here.
admin.site.register(Player)
admin.site.register(CashLog, CashLogAdmin)
