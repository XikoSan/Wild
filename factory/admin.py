from django.contrib import admin
from factory.models.production_log import ProductionLog
from factory.models.auto_produce import AutoProduce

from factory.models.factory.factory import Factory
from factory.models.factory.workshop import Workshop
from factory.models.factory.workplace import Workplace

from factory.models.blueprint import Blueprint
from factory.models.component import Component

# Register your models here.

class ProductionLogAdmin(admin.ModelAdmin):
    model = ProductionLog
    search_fields = ['player__nickname', 'prod_storage__region__region_name']
    raw_id_fields = ('player', 'prod_storage',)
    list_display = ['dtime', 'get_owner_nickname', 'get_good_move', 'prod_value', 'get_good_name', 'get_region_name', ]

    def get_owner_nickname(self, obj):
        return obj.player.nickname

    def get_good_move(self, obj):
        if obj.good_move == 'incom':
            return '🟢'
        elif obj.good_move == 'outcm':
            return '🔴'

    def get_region_name(self, obj):
        return obj.prod_storage.region.region_name

    def get_good_name(self, obj):
        if obj.cash:
            return 'Наличные'
        else:
            if obj.good:
                return obj.good.name
            else:
                return obj.get_old_good_display()


class FactoryAdmin(admin.ModelAdmin):
    model = Factory
    search_fields = ['title', 'owner__nickname', 'region__region_name']
    raw_id_fields = ('owner', 'region',)
    list_display = ['title', 'get_owner_nickname', 'get_region_name', 'level', ]

    def get_owner_nickname(self, obj):
        return obj.owner.nickname

    def get_region_name(self, obj):
        return obj.region.region_name


class WorkshopAdmin(admin.ModelAdmin):
    model = Workshop
    search_fields = ['factory__title', 'good']
    raw_id_fields = ('factory',)
    list_display = ['get_factory_title', 'good', ]

    def get_factory_title(self, obj):
        return obj.factory.title


class WorkplaceAdmin(admin.ModelAdmin):
    model = Workplace
    search_fields = ['worker__nickname', ]
    raw_id_fields = ('worker',)
    list_display = ['worker', 'get_job_title', ]

    def get_job_title(self, obj):
        workplace_class = obj.content_type.model_class()

        if workplace_class.objects.filter(pk=obj.object_id).exists():
            return str(workplace_class.objects.get(pk=obj.object_id))
        else:
            return ''


class AutoProduceAdmin(admin.ModelAdmin):
    model = AutoProduce
    search_fields = ['player__nickname', ]
    raw_id_fields = ('player','storage', 'task',)
    list_display = ['player', 'get_good_name', ]

    def get_good_name(self, obj):
        return obj.good.name
    # def get_job_title(self, obj):
    #     workplace_class = obj.content_type.model_class()
    #
    #     if workplace_class.objects.filter(pk=obj.object_id).exists():
    #         return str(workplace_class.objects.get(pk=obj.object_id))
    #     else:
    #         return ''

class ComponentInline(admin.TabularInline):
    model = Component


class BlueprintAdmin(admin.ModelAdmin):
    model = Blueprint
    search_fields = ['name', 'good__name', ]
    raw_id_fields = ('good', )
    list_display = ['get_good_name', 'get_name', 'energy_cost',  'cash_cost', ]
    inlines = [ComponentInline]

    def get_good_name(self, obj):
        return obj.good.name

    def get_name(self, obj):
        ret = None
        if obj.name:
            ret = obj.name

        elif Component.objects.filter(blueprint=obj).exists():
            for comp in Component.objects.filter(blueprint=obj):
                if not ret:
                    ret = f'{comp.count} {comp.good.name}'
                else:
                    ret += f', {comp.count} {comp.good.name}'

        else:
            ret += f'{obj.good.name} {obj.pk}'

        return ret



class ComponentAdmin(admin.ModelAdmin):
    model = Component
    search_fields = ['blueprint__name', 'good__name', ]
    raw_id_fields = ('good', )
    list_display = ['get_blueprint_name', 'get_good_name', 'count', ]

    def get_blueprint_name(self, obj):
        ret = None
        if obj.blueprint.name:
            ret = obj.blueprint.name

        elif Component.objects.filter(blueprint=obj.blueprint).exists():
            for comp in Component.objects.filter(blueprint=obj.blueprint):
                if not ret:
                    ret = f'{comp.count} {comp.good.name}'
                else:
                    ret += f', {comp.count} {comp.good.name}'

        else:
            ret += f'{obj.blueprint.good.name} {obj.blueprint.pk}'

        return ret

    def get_good_name(self, obj):
        return obj.good.name



admin.site.register(ProductionLog, ProductionLogAdmin)
admin.site.register(Factory, FactoryAdmin)
admin.site.register(Workshop, WorkshopAdmin)
admin.site.register(Workplace, WorkplaceAdmin)
admin.site.register(AutoProduce, AutoProduceAdmin)

admin.site.register(Blueprint, BlueprintAdmin)
admin.site.register(Component, ComponentAdmin)