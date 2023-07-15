from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models

from storage.models.auction.auction import BuyAuction
from storage.models.auction.auction_bet import AuctionBet
from storage.models.auction.auction_lot import AuctionLot
from storage.models.cash_lock import CashLock
from storage.models.destroy import Destroy
from storage.models.good_lock import GoodLock
from storage.models.storage import Storage
from storage.models.trade_offer import TradeOffer
from storage.models.trading_log import TradingLog
from storage.models.transport import Transport
from storage.models.good import Good
from storage.models.stock import Stock
from modeltranslation.admin import TabbedTranslationAdmin

class TradeOfferAdmin(admin.ModelAdmin):
    exclude = ('accepters',)

    search_fields = ['player__nickname']
    raw_id_fields = ('owner_storage',)
    list_display = ('owner_storage', 'type', 'good', 'price', 'deleted')
    list_filter = ('deleted',)

    # formfield_overrides = {
    #     models.ManyToManyField: {'widget': widgets.FilteredSelectMultiple(verbose_name='Принявшие ордер',
    #                                                                       is_stacked=False)},
    # }


class GoodAdmin(TabbedTranslationAdmin):
    list_tabs = ['name',]
    list_display = ['name', 'type', 'size', 'volume', ]
    list_filter = ('type', 'size',)


class StockAdmin(admin.ModelAdmin):
    search_fields = ['good__name', '=storage__pk',]
    raw_id_fields = ('storage', 'good',)
    list_display = ['storage', 'stock', 'get_good', ]

    def get_good(self, obj):
        return obj.good.name

class TransportAdmin(admin.ModelAdmin):
    model = Transport
    raw_id_fields = ('storage_from', 'storage_to', 'good',)

class GoodLockAdmin(admin.ModelAdmin):
    model = GoodLock
    search_fields = ['lock_good', 'lock_count']
    raw_id_fields = ('lock_storage', 'lock_offer',)
    list_display = ['get_owner_nickname', 'get_region_name', 'lock_count', 'lock_good', 'deleted', ]

    def get_owner_nickname(self, obj):
        return obj.lock_storage.owner.nickname

    def get_region_name(self, obj):
        return obj.lock_storage.region.region_name


class StorageAdmin(admin.ModelAdmin):
    search_fields = ['owner__nickname', 'region__region_name']
    raw_id_fields = ('owner', 'region',)
    list_display = ['owner', 'region', ]

    fields = ['get_fields',]

    def get_fields(self, req, obj):
        fields = (
            ('owner', 'region'),
            ('deleted'),
            ('level', 'was_moved'),
            ('cash'),
        )
        for type in Storage.types:
            for good in getattr(Storage, type):
                fields = fields + ((good, good + '_cap'),)

        return fields


class CashLockAdmin(admin.ModelAdmin):
    raw_id_fields = ('lock_player', 'lock_offer',)


class BuyAuctionAdmin(admin.ModelAdmin):
    raw_id_fields = ('treasury_lock',)

    list_display = ['get_state_title', 'good', 'create_date', ]

    def get_state_title(self, obj):
        return obj.treasury_lock.lock_treasury.state.title

    get_state_title.short_description = 'Казна'


class AuctionLotAdmin(admin.ModelAdmin):
    raw_id_fields = ('auction',)

    search_fields = ['auction__pk']

    list_display = ['get_good', 'count', ]

    def get_good(self, obj):
        return obj.auction.get_good_display()

    get_good.short_description = 'Товар'


class AuctionBetAdmin(admin.ModelAdmin):
    raw_id_fields = ('auction_lot', 'good_lock',)

    search_fields = ['auction_lot__pk']

    list_display = ['get_good', 'price', ]

    def get_good(self, obj):
        return obj.auction_lot.auction.get_good_display()

    get_good.short_description = 'Товар'


# Register your models here.
admin.site.register(Good, GoodAdmin)
# admin.site.register(Stock)
admin.site.register(Stock, StockAdmin)
admin.site.register(Storage, StorageAdmin)
admin.site.register(Transport, TransportAdmin)
admin.site.register(Destroy)
admin.site.register(TradeOffer, TradeOfferAdmin)
admin.site.register(GoodLock, GoodLockAdmin)
admin.site.register(CashLock, CashLockAdmin)
admin.site.register(TradingLog)
admin.site.register(AuctionLot, AuctionLotAdmin)
admin.site.register(AuctionBet, AuctionBetAdmin)
admin.site.register(BuyAuction, BuyAuctionAdmin)
