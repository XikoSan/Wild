# Generated by Django 3.1.3 on 2022-10-07 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0028_playersettings_party_back'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='daily_fin',
            field=models.BooleanField(default=False, verbose_name='Дейлик пройден'),
        ),
    ]
