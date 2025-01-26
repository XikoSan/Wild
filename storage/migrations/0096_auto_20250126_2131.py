# Generated by Django 3.2.18 on 2025-01-26 18:31

from django.db import migrations
import random
from datetime import datetime, timedelta
import pytz
from django.apps import apps
from django.utils import timezone

# генератор одного символа
def rotate_spinner():
    weights = [
        0.1,  # джекпот
        1,  # 300к
        3,  # 100к
        10,  # 60к
        20,  # 40к
        70.9,  # 20к
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

    spins = {1: rotate_spinner(), 2: rotate_spinner(), 3: rotate_spinner()}

    results = list(spins.values())

    reward = 0

    # Проверяем, совпадают ли все значения
    if len(results) > 0 and len(set(results)) == 1:

        if list(set(results))[0] == 'disk':
            return 100000000

    for result in results:
        reward += rewards[result]

    return reward


def open_lootboxes(apps, schema_editor):

    Lootbox = apps.get_model("player", "Lootbox")    
    Player = apps.get_model("player", "Player")
    
    CashLog = apps.get_model("player", "CashLog")
    
    for box in Lootbox.objects.filter(stock__gt=0):        
        
        # получаем персонажа игрока
        player = Player.objects.get(pk=box.player.pk)


        for box_count in range(box.stock):

            reward = generate_rewards()

            if reward > 0:
                player.cash += reward

                cash_log = CashLog(player=player, cash=reward, activity_txt='box')
                cash_log.save()

                player.save()

            box.stock -= 1
            box.opened += 1
            
        box.save()        



class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0095_alter_lootboxprize_color'),
    ]

    operations = [
        migrations.RunPython(open_lootboxes),
    ]
