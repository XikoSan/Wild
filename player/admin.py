from re import findall

from django.contrib import admin

from party.position import PartyPosition
from player.logs.cash_log import CashLog
from player.logs.gold_log import GoldLog
from player.logs.skill_training import SkillTraining
from .player import Player


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


class GoldLogAdmin(admin.ModelAdmin):
    list_display = ('player', 'gold', 'activity_txt')
    list_filter = ('activity_txt',)
    search_fields = ('player__nickname',)
    raw_id_fields = ('player',)
    date_hierarchy = 'dtime'
    ordering = ('-dtime',)


class PLayerAdmin(admin.ModelAdmin):
    search_fields = ['nickname', 'user_ip']
    raw_id_fields = ('account', 'party',)

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
admin.site.register(CashLog, CashLogAdmin)
admin.site.register(GoldLog, GoldLogAdmin)
admin.site.register(SkillTraining, SkillTrainingAdmin)
