import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.apps import apps
import json
import redis
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.translation import pgettext
from player.decorators.player import check_player
from player.lootbox.lootbox import Lootbox
from player.player import Player
from player.player_settings import PlayerSettings
from storage.views.vault.avia_box.generate_rewards import generate_rewards
from wild_politics.settings import JResponse
from django.contrib.humanize.templatetags.humanize import number_format
from region.models.plane import Plane
from storage.models.lootbox_prize import LootboxPrize


# Открыть лутбоксы
@login_required(login_url='/')
@check_player
def open_aviaboxes(request):
    if request.method == "POST":
        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        if not Lootbox.objects.filter(player=player, stock__gt=0).exists():
            data = {
                'response': pgettext('open_box', 'У вас нет кейсов'),
                'header': pgettext('open_box', 'Открытие кейсов'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        lootboxes = Lootbox.objects.get(player=player)

        CashLog = apps.get_model('player.CashLog')

        spins, reward = generate_rewards()

        # ----------------------------------------

        redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

        key = f'boxes_{player.pk}'

        # Получение текущих данных игрока
        data = redis_client.get(key)
        if data:
            player_data = json.loads(data)
        else:
            player_data = {"expense": 0, "income": 0}

        # Обновление данных
        # player_data["expense"] += expense
        player_data["income"] += reward

        # Сохранение обратно в Redis
        redis_client.set(key, json.dumps(player_data))

        # ----------------------------------------

        key = f'drops_{player.pk}'

        # Получаем текущий список спинов для пользователя
        current_data = redis_client.lrange(key, 0, -1)

        # Преобразуем данные из строки в словарь
        current_data = [eval(item) for item in current_data]

        # Формируем новую запись
        spin_data = spins
        spin_data.append(reward)

        # Добавляем новую запись в локальный список
        current_data.append(spin_data)

        # Ограничиваем количество записей до 10
        if len(current_data) > 10:
            current_data.pop(0)

        # Преобразуем данные обратно в строки
        stringified_data = [str(item) for item in current_data]

        # Полностью заменяем содержимое списка в Redis
        redis_client.delete(key)  # Удаляем старый ключ
        redis_client.rpush(key, *stringified_data)  # Записываем обновлённые данные

        # ----------------------------------------

        if reward > 0:
            player.cash += reward

            cash_log = CashLog(player=player, cash=reward, activity_txt='box')
            cash_log.save()

            player.save()

            reward = f'${number_format(reward)}'

        else:
            reward = 'ничего'

        lootboxes.stock -= 1
        lootboxes.opened += 1
        lootboxes.save()

        data = {
            'response': 'ok',
            'prizes': spins,
            'reward': reward,

            'boxes_count': lootboxes.stock,
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('open_box', 'Открытие кейсов'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
