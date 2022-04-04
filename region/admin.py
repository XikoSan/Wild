from django.contrib import admin

from region.building.hospital import Hospital
from region.neighbours import Neighbours
from region.region import Region


def recount_rating(modeladmin, request, queryset):
    queryset.model.recount_rating()


recount_rating.short_description = 'Пересчитать рейтинг'


class BuildingAdmin(admin.ModelAdmin):
    list_display = ('get_region', 'level', 'top')
    actions = [recount_rating]

    def get_region(self, obj):
        return obj.region.region_name


# Register your models here.
admin.site.register(Region)
admin.site.register(Neighbours)
admin.site.register(Hospital, BuildingAdmin)
