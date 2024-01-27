import bleach
import json
import logging
import pytz
import re
import redis
import math
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from django.apps import apps
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from chat.models.messages.chat import Chat
from chat.models.messages.chat_members import ChatMembers
from chat.models.messages.message_block import MessageBlock
from chat.models.sticker import Sticker
from chat.models.stickers_ownership import StickersOwnership
from player.player import Player
from storage.models.stock import Stock
from storage.models.storage import Storage
from war.models.wars.unit import Unit
from region.models.terrain.terrain_modifier import TerrainModifier
from skill.models.scouting import Scouting
from skill.models.coherence import Coherence


def _get_player(account):
    return Player.objects.select_related('account').get(account=account)


def _get_player_pk(pk):
    return Player.get_instance(pk=pk)


def _get_user(pk):
    return User.objects.prefetch_related('groups').get(pk=pk)


def _get_groups(user):
    return list(user.groups.all().values_list('name', flat=True))


# проверить, существует ли такая война
def _check_has_war(war_type, war_id):
    try:
        war_class = apps.get_model('war', war_type)

    except KeyError:
        return False

    if not war_class.objects.filter(pk=war_id, running=True).exists():
        return False

    return True


# fighter    - боец
# war_type   - класс войны
# war_id     - ID войны
# storage_pk - Склад
# units      - Юниты (словарь)
# side       - Сторона боя
def _check_has_fight(fighter, war_type, war_id, storage_pk, units, side):
    player = Player.objects.get(pk=fighter.pk)

    if player.banned:
        return False, 'Вы заблокированы за нарушения Правил Игры'

    # проверяем, что есть такой тип войны
    try:
        war_class = apps.get_model('war', war_type)

    except KeyError:
        return False, 'Такого вида войн нет'

    # проверяем, что есть такая активная война
    if not war_class.objects.filter(pk=war_id, deleted=False, running=True).exists():
        data = {
            'response': 'Нет такой войны',
            'header': 'Отправка войск',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)

    war = war_class.objects.get(pk=war_id)

    # проверяем что указана атака или защита
    if not side in ['agr', 'def']:
        return False, 'Нет такой стороны боя'

    # проверяем, что игрок в регионе атаки или защиты
    if not player.region in [war.agr_region, war.def_region]:
        return False, 'Вы находитесь вне зоны боевых действий'

    # проверяем, что ID склада - число
    try:
        storage_pk = int(storage_pk)

    except ValueError:
        return False, 'ID склада должен быть числом'

    # проверяем, что у игрока есть склад в регионе местонахождения с переданным ID
    if not Storage.objects.filter(pk=storage_pk, owner=player, region=player.region).exists():
        return False, 'У вас нет склада в регионе местонахождения'

    storage = Storage.objects.get(pk=storage_pk)

    # проверяем наличие юнитов в словаре
    if not units:
        return False, 'Не выбраны войска'

    # logger = logging.getLogger(__name__)
    # try:

    db_units = Unit.objects.all()

    energy_required = 0

    # хотя бы один юнит был отправлен в бой
    has_unit = False

    # По юнитам:
    for unit in units.keys():
        # проверяем, что есть такие юниты
        if not db_units.filter(pk=int(unit)).exists():
            return False, f'Нет юнита с ID {unit}'

        db_unit = db_units.get(pk=int(unit))

        # проверяем, что переданы только числа юнитов
        try:
            units_count = int(units[unit])

        except ValueError:
            units_count = 0
            # return False, 'Количество войск должно быть числом'

        # проверяем, что переданы только положительные числа юнитов
        if 0 > units_count:
            return False, 'Количество войск должно быть положительным числом'

        if not units_count <= 100:
            return False, 'Количество войск должно быть не более 100'

        if units_count > 0:
            has_unit = True

        # Проверяем, что юнитов на складе достаточно
        if not Stock.objects.filter(storage=storage, good=db_unit.good, stock__gte=units_count).exists():
            return False, f'Недостаточно на складе: {db_unit.good.name}'

        energy_required += units_count * db_unit.energy

    if not has_unit:
        return False, 'В бой не отправлен ни один юнит'

    # проверяем, что затраты на энергию меньше текущего запаса
    if player.energy < energy_required:
        return False, 'Недостаточно энергии'

    return True, None

    # except Exception as e:
    #     logger.exception('Произошла нештатная ситуация:')


# fighter    - боец
# war_type   - класс войны
# war_id     - ID войны
# storage_pk - Склад
# units      - Юниты (словарь)
# side       - Сторона боя
def _send_damage(fighter, war_type, war_id, storage_pk, units, side):
    war_class = apps.get_model('war', war_type)

    war = war_class.objects.get(pk=war_id)

    storage = Storage.objects.get(pk=int(storage_pk))
    db_units = Unit.objects.all()

    damage = 0
    energy_required = 0

    agr_damage = 0
    def_damage = 0

    retry_count = 0
    max_retries = 5

    agr_terrains = war.agr_region.terrain.all()
    def_terrains = war.def_region.terrain.all()
    terrain_list = []

    for terrain in agr_terrains:
        terrain_list.append(terrain)

    for terrain in def_terrains:
        if not terrain in terrain_list:
            terrain_list.append(terrain)

    units_pk = [int(string) for string in units.keys()]

    modifiers_dict = {}
    # модификаторы урона для этого набора рельефов
    modifiers = TerrainModifier.objects.filter(terrain__in=terrain_list, unit__in=units_pk)

    for modifier in modifiers:
        if modifier.unit.pk in modifiers_dict.keys():
            modifiers_dict[modifier.unit.pk] = modifiers_dict[modifier.unit.pk] * modifier.modifier
        else:
            modifiers_dict[modifier.unit.pk] = modifier.modifier

    r = redis.StrictRedis(host='redis', port=6379, db=0)

    with transaction.atomic():
        player = Player.objects.select_for_update().get(pk=fighter.pk)

        # списываем вой ска со склада
        for unit in units.keys():
            db_unit = db_units.get(pk=int(unit))

            if not unit in units or units[unit] == '':
                continue

            units_count = int(units[unit])

            stock = Stock.objects.select_for_update().get(storage=storage, good=db_unit.good)

            stock.stock -= units_count
            stock.save()

            unit_dmg = math.floor( (units_count * db_unit.damage) * (1 + player.power/100) )

            # знание местности
            if Scouting.objects.filter(player=player, level__gt=0).exists():
                unit_dmg = Scouting.objects.get(player=player).apply({'dmg': unit_dmg})

            # Слаженность
            if Coherence.objects.filter(player=player, level__gt=0).exists():
                unit_dmg = Coherence.objects.get(player=player).apply({'dmg': unit_dmg, 'units': units})

            mod = 1
            if int(unit) in modifiers_dict:
                mod = float(modifiers_dict[int(unit)])

            damage += math.floor( unit_dmg * mod )
            energy_required += units_count * db_unit.energy


        player.energy_cons(value=energy_required, mul=2)

        # дальше мы пытаемся внести урон в бой. Если не выйдет - то отменим списание войск и выйдем
        # пытаемся отправить урон за сторону
        while retry_count < max_retries:
            # Отслеживание ключа
            r.watch(f'{war_type}_{war_id}_dmg')

            # Получение текущего значения ключа
            side_dmg = r.hget(f'{war_type}_{war_id}_dmg', side)

            if not side_dmg:
                side_dmg = 0

            # Начало транзакции
            pipe = r.pipeline()
            pipe.multi()

            # Изменение значения ключа
            pipe.hset(f'{war_type}_{war_id}_dmg', side, int(float(side_dmg)) + damage)

            try:
                # Выполнение транзакции
                result = pipe.execute()
                break  # Если транзакция выполнена успешно, выходим из цикла

            except redis.WatchError:
                retry_count += 1
                continue

        if retry_count == max_retries:
            transaction.set_rollback(True)
            return damage, True, None, None


    # обновляем урон игрока
    player_dmg = r.hget(f'{war_type}_{war_id}_{side}_dmg', fighter.pk)
    if not player_dmg:
        player_dmg = 0
    # Изменение значения ключа
    r.hset(f'{war_type}_{war_id}_{side}_dmg', fighter.pk, int(float(player_dmg)) + damage)

    # если игрока нет в списке стороны, за которую он влил урон
    if not fighter.pk in [int(string) for string in r.lrange(f'{war_type}_{war_id}_{side}', 0, -1)]:
        # добавляем игрока в лист атакующих/обороняющихся
        r.rpush(f'{war_type}_{war_id}_{side}', fighter.pk)

    agr_damage = r.hget(f'{war_type}_{war_id}_dmg', 'agr')
    if not agr_damage:
        agr_damage = 0
    else:
        agr_damage = int(float(agr_damage))

    def_damage = r.hget(f'{war_type}_{war_id}_dmg', 'def')
    if not def_damage:
        def_damage = 0
    else:
        def_damage = int(float(def_damage))

    return damage, None, agr_damage, def_damage


class WarConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.player = await sync_to_async(_get_player, thread_sensitive=True)(account=self.scope["user"])

        # logger = logging.getLogger(__name__)
        # logger.debug(self.scope['url_route']['kwargs']['room_name'])

        self.war_type = self.scope['url_route']['kwargs']['war_type']
        self.war_id = self.scope['url_route']['kwargs']['war_id']

        self.room_name = f'{self.war_type}_{self.war_id}_{self.player.pk}'
        self.room_group_name = f'{self.war_type}_{self.war_id}'

        if await sync_to_async(_check_has_war, thread_sensitive=True)(
                war_type=self.war_type,
                war_id=int(self.war_id)
        ):

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

        else:
            self.close()

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)

        units = data['units']
        storage = data['storage']
        side = data['side']

        damage = 0

        can_fight, err_mess = await sync_to_async(_check_has_fight, thread_sensitive=True)(
            # игрок
            fighter=self.player,
            # класс войны
            war_type=self.war_type,
            # ID войны
            war_id=int(self.war_id),

            # Склад
            storage_pk=storage,
            # Юниты
            units=units,
            # Сторона боя
            side=side,
        )

        if can_fight:

            damage, err, agr_dmg, def_dmg = await sync_to_async(_send_damage, thread_sensitive=True)(
                # игрок
                fighter=self.player,
                # класс войны
                war_type=self.war_type,
                # ID войны
                war_id=int(self.war_id),

                # Склад
                storage_pk=storage,
                # Юниты
                units=units,
                # Сторона боя
                side=side,
            )

            if not err:

                image_url = '/static/img/nopic.svg'
                if self.player.image:
                    image_url = self.player.image.url

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'damage': damage,
                        'side': side,

                        'image_url': image_url,

                        'agr_dmg': agr_dmg,
                        'def_dmg': def_dmg,
                    }
                )

            else:
                # Сообщить об ошибке
                await self.send(text_data=json.dumps({
                    'payload': 'error',
                    'response': 'Не удалось отправить войска, повторите попытку',
                    'header': 'Отправка войск',
                    'grey_btn': 'Закрыть',
                }))
        else:
            # Сообщить об ошибке
            await self.send(text_data=json.dumps({
                'payload': 'error',
                'response': err_mess,
                'header': 'Отправка войск',
                'grey_btn': 'Закрыть',
            }))

        # for unit in units.keys():
        #     damage += int(units[unit]) * 10

    # Receive message from room group
    async def chat_message(self, event):

        damage = event['damage']

        agr_side = True
        if event['side'] == 'def':
            agr_side = False

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'damage': damage,
            'agr_side': agr_side,

            'image_url': event['image_url'],

            'agr_dmg': event['agr_dmg'],
            'def_dmg': event['def_dmg'],
        }))
