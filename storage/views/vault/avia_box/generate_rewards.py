import datetime
import math
import random
from datetime import timedelta
from django.apps import apps
from django.db.models import Q
from django.db.models import Sum

from player.player import Player
from region.models.plane import Plane


def prepare_plane_lists(quality='common'):

    common_colors = [
        'base',
        'red', 'yellow', 'orange',
        'green', 'dark_blue', 'light_blue',
        'violet',
    ]

    rare_colors = [
        'black', 'pink', 'green_cam', 'blue_cam', 'desert_cam', 'pobeda', 'airball',
    ]

    epic_colors = Plane.gold_colors

    ret_list = []

    for plane in Plane.planes.keys():
        for color in Plane.planes[plane]:
            if plane == 'nagger' and color == 'base':
                continue

            if color in locals()[f'{quality}_colors']:
                ret_list.append([plane, color])

    return ret_list


# генератор открытия
def generate_rewards(player, garant=False):

    # определяем, что будет дропаться
    # определяем какая награда попадет в список
    reward = random.choices(['gold', 'common', 'rare', 'epic'], weights=[33, 55, 11, 1])
    nagrada = reward[0]

    if garant:
        nagrada = 'epic'

    if nagrada == 'gold':
        weights = [50, 3, 0.1, ]
        reward_val = random.choices([1000, 3000, 100000, ], weights=weights)[0]

    else:
        reward_val = random.choices(prepare_plane_lists(nagrada))[0]

        if Plane.objects.filter(player=player, plane=reward_val[0], color=reward_val[1]).exists():

            if nagrada == 'epic':
                reward_val = 5000

            if nagrada == 'rare':
                reward_val = 1000

            if nagrada == 'common':
                reward_val = 500

    return reward_val, nagrada
