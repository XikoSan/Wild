# Generated by Django 3.1.3 on 2022-04-16 21:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0014_auto_20220415_2347'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='premium',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Премиум, до'),
        ),
    ]
