import math
import random
from datetime import datetime, timedelta
from django.apps import apps
import pytz
from django.db.models import Q
from django.db.models import Sum
from player.lootbox.lootbox import Lootbox
from player.player import Player
from region.models.plane import Plane
from player.logs.gold_log import GoldLog

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


# генератор открытия
def generate_rewards(player, garant=False):

    # определяем, что будет дропаться
    # определяем какая награда попадет в список
    if Lootbox.objects.filter(player=player, stock__gt=100).exists():
        reward = random.choices(['gold', 'common', 'rare', 'epic'], weights=[11, 55, 5, 1])
        nagrada = reward[0]
    else:
        reward = random.choices(['gold', 'common', 'rare', 'epic'], weights=[33, 55, 11, 1])
        nagrada = reward[0]

    if garant:
        nagrada = 'epic'

    if nagrada == 'gold':
        date_msk = datetime(2024, 6, 2, 22, 0, 0)
        timezone_msk = pytz.timezone('Europe/Moscow')
        date_msk = timezone_msk.localize(date_msk)

        if GoldLog.objects.filter(player=player, activity_txt='bx_gld', gold=100000, dtime__gt=date_msk).exists():
            weights = [50, 3, ]
            reward_val = random.choices([1000, 3000, ], weights=weights)[0]
        else:
            weights = [50, 3, 0.1, ]
            reward_val = random.choices([1000, 3000, 100000, ], weights=weights)[0]

    else:
        weights = []
        reward_list = prepare_plane_lists(player, nagrada)

        for reward_plane in reward_list:
            if reward_plane[0] == 'beluzzo':
                weights.append(0.1)
            else:
                weights.append(1)

        reward_val = random.choices(reward_list, weights=weights)[0]

        if Plane.objects.filter(player=player, plane=reward_val[0], color=reward_val[1]).exists():

            if nagrada == 'epic':
                reward_val = 5000

            if nagrada == 'rare':
                reward_val = 1000

            if nagrada == 'common':
                reward_val = 500

            nagrada = 'gold'

    return reward_val, nagrada