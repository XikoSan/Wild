# Generated by Django 3.1.3 on 2022-09-03 17:54

from django.db import migrations


def fix_player_paid_sum(apps, schema_editor):

    Player = apps.get_model("player", "Player")

    players = Player.objects.filter(paid_sum__gt=0)

    for player in players:
    
        player.paid_sum = player.paid_sum / 2
        player.save()


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0025_auto_20220824_0126'),
    ]

    operations = [
        migrations.RunPython(fix_player_paid_sum),
    ]
