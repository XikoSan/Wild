from django.contrib import admin
from factory.models.production_log import ProductionLog
# Register your models here.

class ProductionLogAdmin(admin.ModelAdmin):
    model = ProductionLog
    search_fields = ['player__nickname', 'prod_storage__region__region_name']
    raw_id_fields = ('player', 'prod_storage',)
    list_display = ['dtime', 'get_owner_nickname', 'get_good_move', 'prod_value', 'get_good_display', 'get_region_name', ]

    def get_owner_nickname(self, obj):
        return obj.player.nickname

    def get_good_move(self, obj):
        if obj.good_move == 'incom':
            return '🟢'
        elif obj.good_move == 'outcm':
            return '🔴'


    def get_region_name(self, obj):
        return obj.prod_storage.region.region_name


admin.site.register(ProductionLog, ProductionLogAdmin)