# Generated by Django 3.1.3 on 2021-11-21 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0008_auto_20211021_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='energy_consumption',
            field=models.IntegerField(default=0, verbose_name='Расход энергии'),
        ),
    ]
