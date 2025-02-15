# Generated by Django 3.2.18 on 2024-08-25 17:52

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('region', '0057_auto_20240619_2348'),
        ('war', '0036_auto_20240803_0216'),
    ]

    operations = [
        migrations.CreateModel(
            name='Martial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=False, verbose_name='Активно')),
                ('days_left', models.IntegerField(default=0, verbose_name='Прошло дней')),
                ('active_end', models.DateTimeField(blank=True, default=datetime.datetime(2000, 1, 1, 0, 0), null=True, verbose_name='Время завершения ВП')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reg_mart', to='region.region', verbose_name='Регион')),
            ],
            options={
                'verbose_name': 'Активное военное положение',
                'verbose_name_plural': 'Активные военные положения',
            },
        ),
    ]
