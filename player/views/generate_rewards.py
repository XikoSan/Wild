from player.player import Player
import random

# генератор открытия
def generate_rewards():
    # выбираем количество получаемых игроком наград
    count = random.choices([1, 2, 3,], weights=[70, 20, 10,])

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
                    weights.append(5)

                if element == 'premium':
                    weights.append(10)

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

            weights = [55, 35, 9, 1,]

            reward_sum = random.choices([500, 1000, 3000, 100000, ], weights=weights)

        if nagrada == 'premium':

            weights = [60, 30, 9, 1,]

            reward_sum = random.choices([14, 30, 90, 365, ], weights=weights)

        if nagrada == 'wild_pass':

            weights = [60, 30, 9, 1,]

            reward_sum = random.choices([1, 3, 5, 10, ], weights=weights)

        rewards_summs.append(reward_sum[0])

    return rewards, rewards_summs
