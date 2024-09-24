from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib import admin
from django.db import models
from django.db import transaction
from django.utils import timezone
from re import findall
from tabbed_admin import TabbedModelAdmin

from party.position import PartyPosition
from player.bonus_code.bonus_code import BonusCode
from player.bonus_code.code_usage import CodeUsage
from player.game_event.energy_spent import EnergySpent
from player.game_event.event_part import EventPart
from player.game_event.game_event import GameEvent
from player.game_event.global_part import GlobalPart
from player.logs.auto_mining import AutoMining
from player.logs.cash_log import CashLog
from player.logs.donut_log import DonutLog
from player.logs.gold_log import GoldLog
from player.logs.prem_log import PremLog
from player.logs.skill_training import SkillTraining
from player.logs.wildpass_log import WildpassLog
from player.lootbox.lootbox import Lootbox
from player.player_regional_expence import PlayerRegionalExpense
from .player import Player
from .player_settings import PlayerSettings
from player.logs.test_log import TestLog


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

        prem_log = PremLog(player=player, days=30, activity_txt='buying')
        prem_log.save()


add_premium_month.short_description = 'Добавить 1 месяц према'


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

        prem_log = PremLog(player=player, days=90, activity_txt='buying')
        prem_log.save()


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

        prem_log = PremLog(player=player, days=180, activity_txt='buying')
        prem_log.save()


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
    search_fields = ('player__nickname', 'gold',)
    raw_id_fields = ('player',)
    date_hierarchy = 'dtime'
    ordering = ('-dtime',)


class PremLogAdmin(admin.ModelAdmin):
    list_display = ('player', 'days', 'activity_txt')
    list_filter = ('activity_txt',)
    search_fields = ('player__nickname',)
    raw_id_fields = ('player',)
    date_hierarchy = 'dtime'
    ordering = ('-dtime',)


class WildpassLogAdmin(admin.ModelAdmin):
    list_display = ('player', 'count', 'activity_txt')
    list_filter = ('activity_txt',)
    search_fields = ('player__nickname',)
    raw_id_fields = ('player',)
    date_hierarchy = 'dtime'
    ordering = ('-dtime',)


class PlayerSettingsAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname', ]
    raw_id_fields = ('player',)


class PlayerRegionalExpenseAdmin(admin.ModelAdmin):
    list_display = ('player', 'region', 'energy_consumption')
    search_fields = ['player__nickname', 'region__region_name', ]
    raw_id_fields = ('player', 'region',)


class EventPartAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname', ]
    raw_id_fields = ('player', 'event')


class GlobalPartAdmin(admin.ModelAdmin):
    raw_id_fields = ('event',)


class EnergySpentAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname', ]
    raw_id_fields = ('player',)


class DonutLogAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname', ]
    list_display = ('player', 'dtime')
    raw_id_fields = ('player',)


class LootboxAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname', ]
    list_display = ('player', 'stock')
    raw_id_fields = ('player',)


class PLayerAdminForm(forms.ModelForm):
    # Дополнительные поля для сложения и вычитания
    add_value = forms.IntegerField(label="Добавить", required=False)
    subtract_value = forms.IntegerField(label="Вычесть", required=False)

    class Meta:
        model = Player
        fields = '__all__'


class PLayerAdmin(TabbedModelAdmin):
    form = PLayerAdminForm

    search_fields = ['nickname', 'user_ip', 'fingerprint', 'party__title']
    raw_id_fields = ('account', 'party', 'region', 'residency',)
    list_filter = ('utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', )

    tab_overview = (
        ('Профиль', {
            'fields': ('nickname', 'account', 'image')
        }),
        ('Баны', {
            'fields': ('banned', 'reason', 'chat_ban', 'articles_ban')
        }),
        ('Регион', {
            'fields': ('region', 'residency', 'residency_date')
        }),
        ('Партия', {
            'fields': ('party', 'party_post')
        }),
        ('О себе', {
            'fields': ('bio',)
        })
    )
    tab_storage = (
        ('Кошелёк', {
            'fields': ('cash', 'gold', 'bottles',)
        }),
        ('Изменение баланса золота', {
            'fields': ('add_value', 'subtract_value', )
        }),
        ('Премиум-аккаунт', {
            'fields': ('premium', 'cards_count',)
        }),
    )
    tab_energy = (
        ('Запасы', {
            'fields': ('energy', 'last_refill')
        }),
        ('Прирост', {
            'fields': ('natural_refill', 'last_top')
        }),
    )
    tab_daily = (
        ('Энергия', {
            'fields': ('daily_fin', 'energy_consumption', 'paid_consumption', 'paid_sum')
        }),
    )
    tab_skills = (
        ('Навыки', {
            'fields': ('power', 'knowledge', 'endurance')
        }),
    )
    # tab_settings = (
    #     PlayerSettingsInline,
    # )
    tab_tech = (
        ('Техническое', {
            'fields': ('user_ip', 'fingerprint', 'time_zone', 'educated')
        }),
    )
    tab_flying = (
        ('Регион', {
            'fields': ('destination',)
        }),
        ('Время', {
            'fields': ('arrival',)
        }),
        ('Задача', {
            'fields': ('task',)
        }),
    )
    tab_adv = (
        ('Реклама', {
            'fields': ('utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term')
        }),
    )

    tabs = [
        ('Основные', tab_overview),
        ('Склад', tab_storage),
        ('Энергия', tab_energy),
        ('Дейлик', tab_daily),
        ('Навыки', tab_skills),
        ('Перелёты', tab_flying),
        # ('Настройки', tab_settings),
        ('Техническое', tab_tech),
        ('Реклама', tab_adv),
    ]

    actions = [
        add_premium_month,
        add_3_premium_month,
        add_6_premium_month,
    ]

    # Переопределяем метод сохранения модели, чтобы учесть дополнительные поля
    def save_model(self, request, obj, form, change):
        add_value = form.cleaned_data.get('add_value')
        subtract_value = form.cleaned_data.get('subtract_value')

        if add_value:
            obj.gold += add_value

        if subtract_value:
            obj.gold -= subtract_value

        # Сохраняем изменения в базе данных
        obj.save()

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


class CodeUsageInline(admin.TabularInline):
    model = CodeUsage


class BonusCodeAdmin(admin.ModelAdmin):
    search_fields = ['code', 'premium', 'gold', 'wild_pass', 'cash', ]
    list_display = ('get_name', 'reusable', 'date')
    list_filter = ('premium', 'gold', 'wild_pass', 'cash',)

    inlines = [CodeUsageInline]

    def get_name(self, obj):
        return obj.__str__()


class CodeUsageAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname', ]
    list_display = ('code', 'player')
    raw_id_fields = ('player', 'code',)


class TestLogAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname', ]
    list_display = ('player', 'dtime')
    raw_id_fields = ('player', )


# Register your models here.
admin.site.register(Player, PLayerAdmin)
admin.site.register(PlayerSettings, PlayerSettingsAdmin)
admin.site.register(PlayerRegionalExpense, PlayerRegionalExpenseAdmin)
admin.site.register(CashLog, CashLogAdmin)
admin.site.register(GoldLog, GoldLogAdmin)
admin.site.register(PremLog, PremLogAdmin)
admin.site.register(WildpassLog, WildpassLogAdmin)
admin.site.register(DonutLog, DonutLogAdmin)
admin.site.register(SkillTraining, SkillTrainingAdmin)
admin.site.register(AutoMining, AutoMiningAdmin)

admin.site.register(GameEvent)
admin.site.register(EventPart, EventPartAdmin)
admin.site.register(GlobalPart, GlobalPartAdmin)

admin.site.register(EnergySpent, EnergySpentAdmin)

admin.site.register(Lootbox, LootboxAdmin)

admin.site.register(BonusCode, BonusCodeAdmin)
admin.site.register(CodeUsage, CodeUsageAdmin)

admin.site.register(TestLog, TestLogAdmin)
