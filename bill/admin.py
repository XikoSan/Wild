from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models
from django_celery_beat.models import PeriodicTask

from bill.models.change_coat import ChangeCoat
from bill.models.change_form import ChangeForm
from bill.models.change_residency import ChangeResidency
from bill.models.change_taxes import ChangeTaxes
from bill.models.change_title import ChangeTitle
from bill.models.construction import Construction
from bill.models.explore_all import ExploreAll
from bill.models.explore_all_region import ExploreAllRegion
from bill.models.explore_resources import ExploreResources
from bill.models.geological_surveys import GeologicalSurveys
from bill.models.independence import Independence
from bill.models.martial_law import MartialLaw
from bill.models.purchase_auction import PurchaseAuction
from bill.models.start_war import StartWar
from bill.models.transfer_accept import TransferAccept
from bill.models.transfer_region import TransferRegion
from bill.models.transfer_resources import TransferResources


def recount_rating(modeladmin, request, queryset):
    for bill in queryset:
        bill.do_bill()

        task_identificator = bill.task.id
        # убираем таску у экземпляра модели
        queryset.model.objects.select_related('task').filter(pk=bill.pk).update(task=None)
        # удаляем таску
        PeriodicTask.objects.filter(pk=task_identificator).delete()


recount_rating.short_description = 'Выполнить досрочно'


class BillAdmin(admin.ModelAdmin):
    search_fields = ['initiator', 'parliament']

    list_filter = ("running", "type",)

    list_display = ['get_obj_name', 'running', 'type', ]

    actions = [recount_rating]

    def get_obj_name(self, obj):
        return obj.__str__()

    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.FilteredSelectMultiple(
            verbose_name='Голоса',
            is_stacked=False
        )},
    }


class ExploreAllRegionInline(admin.TabularInline):
    model = ExploreAllRegion


class ExploreAllAdmin(BillAdmin):
    search_fields = ['parliament__state__title', ]
    raw_id_fields = ('parliament', 'task',)
    list_display = ['parliament', 'running', 'resource', 'exp_value', ]
    inlines = [ExploreAllRegionInline]


class ExploreAllRegionAdmin(admin.ModelAdmin):
    search_fields = ['exp_bill__parliament__state__title', 'region__region_name', ]
    raw_id_fields = ('exp_bill', 'region',)
    list_display = ['exp_bill', 'region', 'exp_value', ]


class TransferResourcesAdmin(BillAdmin):
    raw_id_fields = ('send_good', 'send_treasury', 'take_treasury',)


class AuctionAdmin(BillAdmin):
    list_display = ('voting_start', 'good', 'buy_value', 'cash_cost')


# Register your models here.
admin.site.register(ExploreResources, BillAdmin)
admin.site.register(ExploreAll, ExploreAllAdmin)
admin.site.register(ExploreAllRegion, ExploreAllRegionAdmin)
# admin.site.register(GeologicalSurveys, BillAdmin) # этот тип ЗП выключен
admin.site.register(Construction, BillAdmin)
admin.site.register(ChangeTitle, BillAdmin)
admin.site.register(ChangeCoat, BillAdmin)
admin.site.register(ChangeTaxes, BillAdmin)
admin.site.register(ChangeForm, BillAdmin)
admin.site.register(ChangeResidency, BillAdmin)
admin.site.register(StartWar, BillAdmin)
admin.site.register(PurchaseAuction, AuctionAdmin)
admin.site.register(Independence, BillAdmin)
admin.site.register(TransferRegion, BillAdmin)
admin.site.register(TransferAccept, BillAdmin)
admin.site.register(MartialLaw, BillAdmin)
admin.site.register(TransferResources, BillAdmin)
