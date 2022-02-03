from re import findall

from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models

from region.region import Region
from state.models.bills.change_coat import ChangeCoat
from state.models.bills.change_title import ChangeTitle
from state.models.bills.construction import Construction
from state.models.bills.explore_resources import ExploreResources
from state.models.bills.purchase_auction import PurchaseAuction
from state.models.capital import Capital
from state.models.parliament.bulletin import Bulletin
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.parliament.parliament_party import ParliamentParty
from state.models.parliament.parliament_voting import ParliamentVoting
from state.models.state import State
from state.models.treasury import Treasury
from state.models.treasury_lock import TreasuryLock


class CapitalAdmin(admin.ModelAdmin):
    list_display = ('state', 'region')
    raw_id_fields = ('state',)

    # Функциия для отображения у столицы только тех регионов,
    # которые относятся к текущему государству
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Если поле - пост игрока в клане
        if db_field.name == 'region':
            # Получаем pk игрока, запись которого редактируем из пути к редактируемой модели
            # Если метод не change, а add, цифры в пути не будет
            pks = findall(r'/\d+/', request.path)
            # Если цифра найдена
            if pks:
                # Получаем pk(без "/" в начале и конце
                pk = pks[0][1:-1]
                if Capital.objects.filter(pk=pk).exists():
                    capital_ins = Capital.objects.get(pk=pk)
                    # Возвращаем для выбора только те посты, которые относятся к клану игрока
                    kwargs['queryset'] = Region.objects.filter(state=capital_ins.state)
            # Если нет - это значит, что мы не запрашиваем доступ к модели,
            # а значит - создаем новую, pk у которой при создании пока нет
            else:
                # Значит возвращаем пустой список с кланами для "выбора"
                kwargs['queryset'] = Region.objects.none()

        return super(CapitalAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ParliamentVotingAdmin(admin.ModelAdmin):
    list_display = ('parliament', 'voting_start', 'voting_end', 'running')


class DeputyMandateAdmin(admin.ModelAdmin):
    list_display = ('party', 'player', 'parliament')
    raw_id_fields = ('party', 'player', 'parliament')


class BillAdmin(admin.ModelAdmin):
    search_fields = ['initiator', 'parliament']
    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.FilteredSelectMultiple(
            verbose_name='Голоса',
            is_stacked=False
        )},
    }


class AuctionAdmin(BillAdmin):
    list_display = ('voting_start', 'good', 'buy_value', 'cash_cost')


class TreasuryLockAdmin(admin.ModelAdmin):
    model = TreasuryLock
    list_display = ['get_state_title', 'lock_good', 'lock_count', ]

    def get_state_title(self, obj):
        return obj.lock_treasury.state.title

    get_state_title.short_description = 'Казна'


# Register your models here.
admin.site.register(State)
admin.site.register(Treasury)
admin.site.register(TreasuryLock, TreasuryLockAdmin)
admin.site.register(Parliament)
admin.site.register(ParliamentVoting, ParliamentVotingAdmin)
admin.site.register(Bulletin)
admin.site.register(DeputyMandate, DeputyMandateAdmin)
admin.site.register(ParliamentParty)
admin.site.register(Capital, CapitalAdmin)

admin.site.register(ExploreResources, BillAdmin)
admin.site.register(Construction, BillAdmin)
admin.site.register(ChangeTitle, BillAdmin)
admin.site.register(ChangeCoat, BillAdmin)
admin.site.register(PurchaseAuction, AuctionAdmin)
