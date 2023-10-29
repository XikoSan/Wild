from re import findall

from django.contrib import admin
from django.db import transaction
from party.position import PartyPosition
from player.logs.cash_log import CashLog
from player.logs.gold_log import GoldLog
from player.logs.skill_training import SkillTraining
from player.logs.auto_mining import AutoMining
from .player import Player
from .player_settings import PlayerSettings
from player.game_event.game_event import GameEvent
from player.game_event.event_part import EventPart
from player.game_event.global_part import GlobalPart
from django.utils import timezone
from player.player_regional_expence import PlayerRegionalExpense
from player.game_event.energy_spent import EnergySpent
from player.logs.donut_log import DonutLog
from dateutil.relativedelta import relativedelta

@transaction.atomic
def add_premium_month(modeladmin, request, queryset):
    for player in queryset:
        # время, к которому прибавляем месяц
        if player.premium > timezone.now():
            from_time = player.premium
        else:
            from_time = timezone.now()

        player.premium = from_time + relativedelta(months=1)

        player.save()

add_premium_month.short_description = 'Добавить 1 месяц према'\


@transaction.atomic
def add_3_premium_month(modeladmin, request, queryset):
    for player in queryset:
        # время, к которому прибавляем месяц
        if player.premium > timezone.now():
            from_time = player.premium
        else:
            from_time = timezone.now()

        player.premium = from_time + relativedelta(months=3)

        player.save()

add_3_premium_month.short_description = 'Добавить 3 месяца према'


@transaction.atomic
def add_6_premium_month(modeladmin, request, queryset):
    for player in queryset:
        # время, к которому прибавляем месяц
        if player.premium > timezone.now():
            from_time = player.premium
        else:
            from_time = timezone.now()

        player.premium = from_time + relativedelta(months=6)

        player.save()

add_6_premium_month.short_description = 'Добавить 6 месяцев према'


class CashLogAdmin(admin.ModelAdmin):
    list_display = ('player', 'cash', 'activity_txt')
    list_filter = ('activity_txt',)
    search_fields = ('player__nickname',)
    raw_id_fields = ('player',)
    date_hierarchy = 'dtime'
    ordering = ('-dtime',)


class SkillTrainingAdmin(admin.ModelAdmin):
    list_display = ('player', 'skill', 'end_dtime')
    list_filter = ('skill',)
    search_fields = ('player__nickname',)
    raw_id_fields = ('player',)
    date_hierarchy = 'dtime'
    ordering = ('-dtime',)


class AutoMiningAdmin(admin.ModelAdmin):
    list_display = ('player', 'resource', 'dtime')
    list_filter = ('resource',)
    search_fields = ('player__nickname',)
    raw_id_fields = ('player',)
    date_hierarchy = 'dtime'
    ordering = ('-dtime',)


class GoldLogAdmin(admin.ModelAdmin):
    list_display = ('player', 'gold', 'activity_txt')
    list_filter = ('activity_txt',)
    search_fields = ('player__nickname',)
    raw_id_fields = ('player',)
    date_hierarchy = 'dtime'
    ordering = ('-dtime',)


class PlayerSettingsAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname',]
    raw_id_fields = ('player',)


class PlayerRegionalExpenseAdmin(admin.ModelAdmin):
    list_display = ('player', 'region', 'energy_consumption')
    search_fields = ['player__nickname', 'region__region_name',]
    raw_id_fields = ('player', 'region',)


class EventPartAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname', ]
    raw_id_fields = ('player', 'event')


class GlobalPartAdmin(admin.ModelAdmin):
    raw_id_fields = ('event', )


class EnergySpentAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname', ]
    raw_id_fields = ('player', )


class DonutLogAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname', ]
    list_display = ('player', 'dtime')
    raw_id_fields = ('player', )


class PLayerAdmin(admin.ModelAdmin):
    search_fields = ['nickname', 'user_ip']
    raw_id_fields = ('account', 'party',)

    actions = [
                    add_premium_month,
                    add_3_premium_month,
                    add_6_premium_month,
    ]

    # Функциия для отображения у игрока только тех постов,
    # которые относятся к текущему клану игрока
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Если поле - пост игрока в клане
        if db_field.name == 'party_post':
            # Получаем pk игрока, запись которого редактируем из пути к редактируемой модели
            # Если метод не change, а add, цифры в пути не будет
            pks = findall(r'/\d+/', request.path)
            # Если цифра найдена
            if pks:
                # Получаем pk(без "/" в начале и конце
                pk = pks[0][1:-1]
                if Player.objects.filter(pk=pk).exists():
                    user = Player.get_instance(pk=pk)
                    # Возвращаем для выбора только те посты, которые относятся к клану игрока
                    kwargs['queryset'] = PartyPosition.objects.filter(party=user.party)
            # Если нет - это значит, что мы не запрашиваем доступ к модели Player,
            # а значит - создаем новую, pk у которой при создании пока нет
            # А если мы создаем нового игрока, то и клана у него пока нет
            else:
                # Значит возвращаем пустой список с кланами для "выбора"
                kwargs['queryset'] = PartyPosition.objects.none()

        return super(PLayerAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


# Register your models here.
admin.site.register(Player, PLayerAdmin)
admin.site.register(PlayerSettings, PlayerSettingsAdmin)
admin.site.register(PlayerRegionalExpense, PlayerRegionalExpenseAdmin)
admin.site.register(CashLog, CashLogAdmin)
admin.site.register(GoldLog, GoldLogAdmin)
admin.site.register(DonutLog, DonutLogAdmin)
admin.site.register(SkillTraining, SkillTrainingAdmin)
admin.site.register(AutoMining, AutoMiningAdmin)

admin.site.register(GameEvent)
admin.site.register(EventPart, EventPartAdmin)
admin.site.register(GlobalPart, GlobalPartAdmin)

admin.site.register(EnergySpent, EnergySpentAdmin)
