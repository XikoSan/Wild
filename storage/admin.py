from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models

from storage.models.auction.auction import BuyAuction
from storage.models.auction.auction_bet import AuctionBet
from storage.models.auction.auction_lot import AuctionLot
from storage.models.cash_lock import CashLock
from storage.models.destroy import Destroy
from storage.models.factory.production_log import ProductionLog
from storage.models.good_lock import GoodLock
from storage.models.storage import Storage
from storage.models.trade_offer import TradeOffer
from storage.models.trading_log import TradingLog
from storage.models.transport import Transport


class TradeOfferAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname']
    list_display = ('owner_storage', 'type', 'good', 'price', 'deleted')
    list_filter = ('deleted',)

    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.FilteredSelectMultiple(verbose_name='Принявшие ордер',
                                                                          is_stacked=False)},
    }


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
    raw_id_fields = ('owner', 'region',)


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
admin.site.register(Storage, StorageAdmin)
admin.site.register(Transport)
admin.site.register(Destroy)
admin.site.register(TradeOffer, TradeOfferAdmin)
admin.site.register(GoodLock, GoodLockAdmin)
admin.site.register(CashLock, CashLockAdmin)
admin.site.register(TradingLog)
admin.site.register(AuctionLot, AuctionLotAdmin)
admin.site.register(AuctionBet, AuctionBetAdmin)
admin.site.register(BuyAuction, BuyAuctionAdmin)
admin.site.register(ProductionLog)
