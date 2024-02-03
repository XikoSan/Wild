import datetime
import math
import random
from datetime import timedelta
from django.apps import apps
from django.db.models import Q
from django.db.models import Sum

from player.player import Player


# генератор открытия
def generate_rewards(player):
    # выбираем количество получаемых игроком наград
    count = random.choices([1, 2, 3, ], weights=[85, 10, 5, ])

    GoldLog = apps.get_model('player.GoldLog')
    PremLog = apps.get_model('player.PremLog')
    WildpassLog = apps.get_model('player.WildpassLog')

    # собираем награды игрока за месяц
    date_now = datetime.datetime.now()
    date_30d = date_now - timedelta(days=30)

    # сколько золота потрачено на лутбоксы
    if GoldLog.objects.filter(
            Q(dtime__gt=date_30d), Q(dtime__lt=date_now),
            activity_txt='boxes', player=player
        ).exists():

        gold_spent = GoldLog.objects.filter(
                                            Q(dtime__gt=date_30d), Q(dtime__lt=date_now),
                                            activity_txt='boxes', player=player
                                        ).aggregate(total_gold=Sum('gold'))['total_gold']
    else:
        gold_spent = 0

    # сколько золота дропалось с ящиков
    if GoldLog.objects.filter(
            Q(dtime__gt=date_30d), Q(dtime__lt=date_now),
            activity_txt='bx_gld', player=player
        ).exists():

        gold_log_summ = \
            GoldLog.objects.filter(
                Q(dtime__gt=date_30d), Q(dtime__lt=date_now),
                activity_txt='bx_gld', player=player
            ).aggregate(total_gold=Sum('gold'))['total_gold']
    else:
        gold_log_summ = 0

    # сколько премиума в эквиваленте золота дропалось с ящиков
    if PremLog.objects.filter(
            Q(dtime__gt=date_30d), Q(dtime__lt=date_now),
            activity_txt='lootbox', player=player
        ).exists():

        prem_log_summ = math.ceil(
            PremLog.objects.filter(
                Q(dtime__gt=date_30d), Q(dtime__lt=date_now),
                activity_txt='lootbox', player=player
            ).aggregate(total_days=Sum('days'))['total_days'] / 30) * 1000
    else:
        prem_log_summ = 0

    # сколько вилдпассов в эквиваленте золота дропалось с ящиков
    if WildpassLog.objects.filter(
            Q(dtime__gt=date_30d), Q(dtime__lt=date_now),
            activity_txt='lootbox', player=player
        ).exists():

        wildpass_log_summ = WildpassLog.objects.filter(
            Q(dtime__gt=date_30d), Q(dtime__lt=date_now),
            activity_txt='lootbox', player=player
        ).aggregate(total_count=Sum('count'))['total_count'] * 1000

    else:
        wildpass_log_summ = 0

    total_reward = gold_log_summ + prem_log_summ + wildpass_log_summ

    bonus_mul = math.ceil( ( gold_spent - total_reward ) / 1000)

    if bonus_mul < 0:
        bonus_mul = 0

    if bonus_mul > 30:
        bonus_mul = 30

    # выбираем какие награды именно игрок получит
    rewards = []
    if count[0] == 3:
        rewards = ['gold', 'premium', 'wild_pass']
    # 1 или 2
    if count[0] < 3:
        # 0, 1 или только 0
        for repeat in range(count[0]):
            total_rewards = ['gold', 'premium', 'wild_pass']

            diff = []
            for element in total_rewards:
                if element not in rewards:
                    diff.append(element)

            # diff = set(total_rewards).symmetric_difference(set(rewards))
            # diff = list(diff)

            weights = []
            for element in diff:

                if element == 'gold':
                    weights.append(15)

                if element == 'premium':
                    weights.append(5)

                if element == 'wild_pass':
                    weights.append(1)

            # определяем какая награда попадет в список
            reward = random.choices(diff, weights=weights)

            rewards.append(reward[0])

    # к этому моменту будет некоторый лист наград,
    # скажем, золото и Wild Pass
    # rewards == ['gold', 'wild_pass']
    # для каждой из наград списка, мы должны определить числовое значение приза

    rewards_summs = []

    for nagrada in rewards:
        reward_sum = 0

        if nagrada == 'gold':
            weights = [84, 10 + bonus_mul*10, 1 + bonus_mul, 0.1 + bonus_mul*0.1, ]

            reward_sum = random.choices([500, 1000, 3000, 100000, ], weights=weights)

        if nagrada == 'premium':
            weights = [80, 10 + bonus_mul*10, 1 + bonus_mul, 0.1 + bonus_mul*0.1, ]

            reward_sum = random.choices([14, 30, 90, 365, ], weights=weights)

        if nagrada == 'wild_pass':
            weights = [91, 5, 1, 0.1, ]

            reward_sum = random.choices([1, 3, 5, 10, ], weights=weights)

        rewards_summs.append(reward_sum[0])

    return rewards, rewards_summs
