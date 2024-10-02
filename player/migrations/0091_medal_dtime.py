# Generated by Django 3.2.18 on 2024-10-02 21:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0090_alter_medal_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='medal',
            name='dtime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Время обновления записи'),
        ),
    ]
