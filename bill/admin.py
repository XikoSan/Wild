from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models

from bill.models.change_coat import ChangeCoat
from bill.models.change_taxes import ChangeTaxes
from bill.models.change_title import ChangeTitle
from bill.models.construction import Construction
from bill.models.explore_resources import ExploreResources
from bill.models.purchase_auction import PurchaseAuction


class BillAdmin(admin.ModelAdmin):
    search_fields = ['initiator', 'parliament']

    list_filter = ("running", "type",)

    list_display = ['get_obj_name', 'running', 'type', ]

    def get_obj_name(self, obj):
        return obj.__str__()

    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.FilteredSelectMultiple(
            verbose_name='Голоса',
            is_stacked=False
        )},
    }


class AuctionAdmin(BillAdmin):
    list_display = ('voting_start', 'good', 'buy_value', 'cash_cost')


# Register your models here.
admin.site.register(ExploreResources, BillAdmin)
admin.site.register(Construction, BillAdmin)
admin.site.register(ChangeTitle, BillAdmin)
admin.site.register(ChangeCoat, BillAdmin)
admin.site.register(ChangeTaxes, BillAdmin)
admin.site.register(PurchaseAuction, AuctionAdmin)
