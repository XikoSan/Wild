from django.contrib import admin
from metrics.models.daily_cash import DailyCash
from metrics.models.daily_oil import DailyOil
from metrics.models.daily_ore import DailyOre

class DailyCashAdmin(admin.ModelAdmin):
    list_display = ('date', 'cash', )
    list_filter = ('date',)
    search_fields = ('date',)
    date_hierarchy = 'date'
    ordering = ('-date',)


class DailyOilAdmin(admin.ModelAdmin):
    list_display = ('date', 'type', 'oil', )
    list_filter = ('date', 'type',)
    search_fields = ('date', 'type',)
    date_hierarchy = 'date'
    ordering = ('-date',)


class DailyOreAdmin(admin.ModelAdmin):
    list_display = ('date', 'type', 'ore', )
    list_filter = ('date', 'type',)
    search_fields = ('date', 'type',)
    date_hierarchy = 'date'
    ordering = ('-date',)


# Register your models here.
admin.site.register(DailyCash, DailyCashAdmin)
admin.site.register(DailyOil, DailyOilAdmin)
admin.site.register(DailyOre, DailyOreAdmin)