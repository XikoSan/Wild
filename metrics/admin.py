from django.contrib import admin
from math import floor

from metrics.models.daily_cash import DailyCash
from metrics.models.daily_gold import DailyGold
from metrics.models.daily_gold_by_state import DailyGoldByState
from metrics.models.daily_oil import DailyOil
from metrics.models.daily_ore import DailyOre


class DailyGoldAdmin(admin.ModelAdmin):
    list_display = ('date', 'gold',)
    list_filter = ('date',)
    search_fields = ('date',)
    date_hierarchy = 'date'
    ordering = ('-date',)


class DailyGoldByStateAdmin(admin.ModelAdmin):
    list_display = ('date', 'state', 'gold', 'daily_gold',)
    raw_id_fields = ('state',)
    list_filter = ('date',)
    search_fields = ('date', 'state',)
    date_hierarchy = 'date'
    ordering = ('-date',)


class DailyCashAdmin(admin.ModelAdmin):
    list_display = ('date', 'cash',)
    list_filter = ('date',)
    search_fields = ('date',)
    date_hierarchy = 'date'
    ordering = ('-date',)


class DailyOilAdmin(admin.ModelAdmin):
    list_display = ('date', 'type', 'oil',)
    list_filter = ('date', 'type',)
    search_fields = ('date', 'type',)
    date_hierarchy = 'date'
    ordering = ('-date',)


class DailyOreAdmin(admin.ModelAdmin):
    list_display = ('date', 'type', 'ore',)
    list_filter = ('date', 'type',)
    search_fields = ('date', 'type',)
    date_hierarchy = 'date'
    ordering = ('-date',)


# Register your models here.
admin.site.register(DailyCash, DailyCashAdmin)
admin.site.register(DailyOil, DailyOilAdmin)
admin.site.register(DailyOre, DailyOreAdmin)
admin.site.register(DailyGold, DailyGoldAdmin)
admin.site.register(DailyGoldByState, DailyGoldByStateAdmin)
