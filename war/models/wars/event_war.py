# coding=utf-8
import datetime
import os
import plotly.graph_objects as go
import pytz
import redis
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import pgettext
from django_celery_beat.models import PeriodicTask

from player.player import Player
from player.player_settings import PlayerSettings
from player.views.timers import interval_in_seconds, format_time
from region.models.terrain.terrain_modifier import TerrainModifier
from skill.models.coherence import Coherence
from skill.models.scouting import Scouting
from storage.models.stock import Stock
from storage.models.storage import Storage
from war.models.wars.player_damage import PlayerDamage
from war.models.wars.unit import Unit
from war.models.wars.war import War
from war.models.wars.war_side import WarSide


# класс ивентовой войны
class EventWar(War):
    # прочность Штаба
    hq_points = models.BigIntegerField(default=0, verbose_name='Прочность Штаба')

    # стороны войны
    war_side = GenericRelation(WarSide)
    # урон в этой войне
    war_damage = GenericRelation(PlayerDamage)

    def __str__(self):
        return 'Тестовая война в регионе ' + getattr(self.agr_region, 'region_name')

    # Свойства класса
    class Meta:
        verbose_name = "Тестовая война"
        verbose_name_plural = "Тестовые войны"

    # просчитать раунд войны
    def war_round(self):
        self.round += 1
        r = redis.StrictRedis(host='redis', port=6379, db=0)

        agr_damage = r.hget(f'{self.__class__.__name__}_{self.pk}_dmg', 'agr')
        if not agr_damage:
            agr_damage = 0
        else:
            agr_damage = int(agr_damage)

        def_damage = r.hget(f'{self.__class__.__name__}_{self.pk}_dmg', 'def')
        if not def_damage:
            def_damage = 0
        else:
            def_damage = int(def_damage)

        self.hq_points = def_damage - agr_damage

        # сохраняем инфу в объектах
        for side in ['agr', 'def']:
            w_side = self.war_side.get(side=side)
            if side == 'agr':
                w_side.count = agr_damage
            else:
                w_side.count = def_damage
            w_side.save()

        # сохраняем очки урона в график
        graph = []
        timestamp = str(datetime.datetime.now().timestamp()).split('.')[0]

        if self.graph:
            graph = eval(self.graph)

            if not graph[-1][1] == self.hq_points:
                graph.append((timestamp, self.hq_points))
        else:
            graph.append((timestamp, self.hq_points))

        self.graph = str(graph)

        self.save()

        player_damage_u = []
        # сохраняем урон игроков
        for side in ['agr', 'def']:

            for fighter in [int(string) for string in r.lrange(f'{self.__class__.__name__}_{self.pk}_{side}', 0, -1)]:
                p_damage, created = PlayerDamage.objects.get_or_create(
                    content_type=ContentType.objects.get_for_model(self.__class__),
                    object_id=self.pk,
                    player=Player.objects.only("pk").get(pk=fighter),
                    side=side,
                )
                p_damage.damage = int(r.hget(f'{self.__class__.__name__}_{self.pk}_{side}_dmg', fighter))

                player_damage_u.append(p_damage)

        if player_damage_u:
            PlayerDamage.objects.bulk_update(
                player_damage_u,
                fields=['damage', ],
                batch_size=len(player_damage_u)
            )

    # завершить войну
    def war_end(self):
        self.war_round()

        pk = self.task.pk
        end_pk = self.end_task.pk

        self.task = None
        self.end_task = None

        self.running = False
        self.end_time = timezone.now()

        self.save()
        PeriodicTask.objects.filter(pk=pk).delete()
        PeriodicTask.objects.filter(pk=end_pk).delete()

        r = redis.StrictRedis(host='redis', port=6379, db=0)
        r.delete(f'{self.__class__.__name__}_{self.pk}_dmg')
        for side in ['agr', 'def']:
            r.delete(f'{self.__class__.__name__}_{self.pk}_{side}')

    def get_page(self, request):
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        premium = False

        if player.premium > timezone.now():
            premium = True

        if not self.running:
            agr_damage = self.war_side.get(side='agr', object_id=self.pk).count
            def_damage = self.war_side.get(side='def', object_id=self.pk).count

        else:

            r = redis.StrictRedis(host='redis', port=6379, db=0)

            agr_damage = r.hget(f'{self.__class__.__name__}_{self.pk}_dmg', 'agr')
            if not agr_damage:
                agr_damage = 0
            else:
                agr_damage = int(agr_damage)

            def_damage = r.hget(f'{self.__class__.__name__}_{self.pk}_dmg', 'def')
            if not def_damage:
                def_damage = 0
            else:
                def_damage = int(def_damage)

        war_countdown = interval_in_seconds(
            object=self,
            start_fname='start_time',
            end_fname=None,
            delay_in_sec=86400
        )

        dtime_str = format_time(war_countdown)

        agr_terrains = self.agr_region.terrain.all()
        def_terrains = self.def_region.terrain.all()
        terrain_list = []

        for terrain in agr_terrains:
            terrain_list.append(terrain)

        for terrain in def_terrains:
            if not terrain in terrain_list:
                terrain_list.append(terrain)

        modifiers_dict = {}
        # модификаторы урона для этого набора рельефов
        modifiers = TerrainModifier.objects.filter(terrain__in=terrain_list)

        for modifier in modifiers:
            if modifier.unit.pk in modifiers_dict.keys():
                modifiers_dict[modifier.unit.pk] = modifiers_dict[modifier.unit.pk] * modifier.modifier
            else:
                modifiers_dict[modifier.unit.pk] = modifier.modifier

        agr_char_list = self.war_damage.filter(object_id=self.pk, side='agr')
        def_char_list = self.war_damage.filter(object_id=self.pk, side='def')

        in_region = False
        storages = []

        units = Unit.objects.all()
        # фактические запасы оружия на доступном складе
        units_dict = {}

        unit_goods = []
        for unit in units:
            unit_goods.append(unit.good)

        if player.region == self.agr_region or player.region == self.def_region:
            in_region = True
            if Storage.actual.filter(owner=player, region=player.region).exists():

                storage = Storage.actual.get(owner=player, region=player.region)
                storages.append(storage)

                weapons = Stock.objects.filter(storage=storage, good__in=unit_goods, stock__gt=0)

                for weapon in weapons:
                    units_dict[weapon.good] = weapon.stock

        # знание местности
        scouting_perk = 0
        if Scouting.objects.filter(player=player, level__gt=0).exists():
            unit_dmg = Scouting.objects.get(player=player).apply({'dmg': 100})
            # если перк не применился, значит, игрок находится менее суток в реге, учитывать не надо
            if unit_dmg > 100:
                scouting_perk = Scouting.objects.get(player=player).level

        # Слаженность
        coherence_perk = False
        if Coherence.objects.filter(player=player, level__gt=0).exists():
            coherence_perk = True

        # --------------------------------------------------------------------------------------------
        # цвет из настроек
        main_color = '#28353E'
        sub_color = '#284E64'
        text_color = '#FFFFFF'
        button_color = '#EB9929'

        if PlayerSettings.objects.filter(player=player).exists():
            setts = PlayerSettings.objects.get(player=player)

            main_color = '#' + str(setts.color_back)
            sub_color = '#' + str(setts.color_block)
            text_color = '#' + str(setts.color_text)
            button_color = '#' + str(setts.color_acct)

        data = []
        graph_html = None
        if self.graph:
            data = eval(self.graph)

        if data:
            # Разделите список на два отдельных списка: timestamps и scores
            timestamps, scores = zip(*data)

            # Преобразуйте значения timestamps в объекты datetime
            timestamps = [datetime.datetime.fromtimestamp(int(timestamp)).astimezone(tz=pytz.timezone(player.time_zone))
                          for timestamp in timestamps]

            # Создайте объект Scatter для значений
            fig = go.Figure()

            # Добавьте единственный объект Scatter для всех значений
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=scores,
                mode='lines+markers',
                line=dict(color=text_color),  # Цвет линии графика
                marker=dict(color=text_color),  # Цвет маркеров
                showlegend=False,  # Отключает отображение в легенде
                hoverinfo='x+y'  # Отображает только время и значение во всплывающем элементе
            ))

            # Настройте макет графика
            fig.update_layout(
                title=dict(
                    text=pgettext('war_page', 'График урона в бою'),
                    font=dict(color=text_color)  # Цвет текста заголовка
                ),
                xaxis=dict(
                    title=dict(text=pgettext('war_page', 'дата/время'), font=dict(color='white')),
                    # Цвет заголовка оси X
                    tickfont=dict(color=text_color),  # Цвет меток оси X
                    gridcolor=sub_color  # Цвет сетки оси X
                ),
                yaxis=dict(
                    title=dict(text=pgettext('war_page', 'очки урона'), font=dict(color='white')),
                    # Цвет заголовка оси Y
                    tickfont=dict(color=text_color),  # Цвет меток оси Y
                    gridcolor=sub_color  # Цвет сетки оси Y
                ),
                plot_bgcolor=main_color,  # Цвет области построения
                paper_bgcolor=main_color,  # Цвет фона бумаги
                font=dict(color=text_color),  # Цвет текста по умолчанию (например, легенды)
                hoverlabel=dict(  # Настройка стиля всплывающего элемента
                    bgcolor=sub_color,  # Цвет фона
                    bordercolor=text_color,  # Цвет рамки
                    font=dict(color=text_color)  # Цвет текста
                ),
                autosize=True,  # Позволяет графику адаптироваться к контейнеру
                margin=dict(l=10, r=10, t=30, b=10),  # Минимальные отступы
            )

            # Преобразуйте график в HTML и сохраните его в переменную
            graph_html = fig.to_html(full_html=False, config={'responsive': True})  # Адаптивность графика
        # --------------------------------------------------------------------------------------------

        http_use = False
        if os.getenv('HTTP_USE'):
            http_use = True

        # отправляем в форму
        return render(request, 'war/redesign/' + self.__class__.__name__ + '.html', {
            # самого игрока
            'player': player,
            'premium': premium,
            # в зоне боевых действий
            'in_region': in_region,
            # склад
            'storages': storages,

            # характеристики юнитов
            'units': units,
            # модификаторы урона для юнитов
            'modifiers_dict': modifiers_dict,
            # оружие
            'units_dict': units_dict,

            # война
            'war': self,
            # модификаторы рельефа
            'terrains': terrain_list,
            # перки
            'coherence_perk': coherence_perk,
            'scouting_perk': scouting_perk,
            # время окончания войны
            'war_countdown': war_countdown,
            # форматированная строка текущего оставшегося времени
            'dtime_str': dtime_str,

            # сторона атаки
            'agr_dmg': agr_damage,
            # сторона обороны
            'def_dmg': def_damage,
            # разница в уроне
            'delta': def_damage - agr_damage,

            # сторона атаки - игроки
            'agr_char_list': agr_char_list,
            # сторона обороны - игроки
            'def_char_list': def_char_list,

            # класс войны
            'war_cl': War,

            'http_use': http_use,

            'graph_html': graph_html

        })


# сигнал прослушивающий создание партии, после этого формирующий таску
@receiver(post_delete, sender=EventWar)
def delete_post(sender, instance, **kwargs):
    if instance.task:
        instance.task.delete()
