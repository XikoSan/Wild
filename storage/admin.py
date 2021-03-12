from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models

from storage.models.cash_lock import CashLock
from storage.models.destroy import Destroy
from storage.models.good_lock import GoodLock
from storage.models.storage import Storage
from storage.models.trade_offer import TradeOffer
from storage.models.trading_log import TradingLog
from storage.models.transport import Transport


class TradeOfferAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname']
    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.FilteredSelectMultiple(verbose_name='Принявшие ордер',
                                                                          is_stacked=False)},
    }


class GoodLockAdmin(admin.ModelAdmin):
    raw_id_fields = ('lock_storage', 'lock_offer',)


class CashLockAdmin(admin.ModelAdmin):
    raw_id_fields = ('lock_player', 'lock_offer',)


# Register your models here.
admin.site.register(Storage)
admin.site.register(Transport)
admin.site.register(Destroy)
admin.site.register(TradeOffer, TradeOfferAdmin)
admin.site.register(GoodLock, GoodLockAdmin)
admin.site.register(CashLock, CashLockAdmin)
admin.site.register(TradingLog)
