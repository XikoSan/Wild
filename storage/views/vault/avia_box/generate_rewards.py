import math
import pytz
import random
from collections import Counter
from datetime import datetime, timedelta
from django.apps import apps
from django.db.models import F
from django.db.models import Q
from django.db.models import Sum

from player.logs.gold_log import GoldLog
from player.lootbox.jackpot import Jackpot
from player.lootbox.lootbox import Lootbox
from player.player import Player
from region.models.plane import Plane


def prepare_plane_lists(player, quality='common'):
    planes = Plane.objects.filter(player=player)

    common_colors = Plane.common_colors
    rare_colors = Plane.rare_colors
    epic_colors = Plane.gold_colors

    ret_list = []

    for plane in Plane.planes.keys():
        for color in Plane.planes[plane]:
            if plane == 'nagger' and color == 'base':
                continue

            if color in locals()[f'{quality}_colors']:
                if planes.filter(plane=plane, color=color).exists():
                    ret_list.append([plane, color, True])
                else:
                    ret_list.append([plane, color, False])

    return ret_list


# генератор одного символа
def rotate_spinner():
    weights = [
        0.1,  # джекпот
        1,    # 300к
        3,    # 100к
        10,   # 60к
        25,     # 40к
        65.9,   # 20к
    ]
    choices = ['disk', 'gold', 'violet', 'blue', 'green', 'white']

    return random.choices(choices, weights=weights)[0]


# генератор приза
def generate_rewards():
    rewards = {
        'disk': 10000,
        'gold': 300000,
        'violet': 100000,
        'blue': 60000,
        'green': 40000,
        'white': 20000,
    }

    # выдаем суперприз
    if not Jackpot.objects.filter(amount__gt=200000).exists():
        jp = Jackpot(amount=10000000)
        jp.save()

    spins = {1: rotate_spinner(), 2: rotate_spinner(), 3: rotate_spinner()}

    results = list(spins.values())

    reward = 0

    # Проверяем, совпадают ли все значения
    if len(results) > 0 and len(set(results)) == 1:

        if list(set(results))[0] == 'disk':
            budget = Jackpot.objects.filter(amount__gt=200000).first()
            budget.amount = math.ceil(budget.amount / 2)
            budget.save()

            return list(spins.values()), math.ceil(budget.amount / 4)

    for result in results:
        reward += rewards[result]

    return results, reward


