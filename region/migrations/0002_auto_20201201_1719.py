# Generated by Django 3.1.3 on 2020-12-01 13:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('region', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='anohor_proc',
            field=models.IntegerField(default=25, verbose_name='Процент Анохора'),
        ),
        migrations.AddField(
            model_name='region',
            name='berkonor_proc',
            field=models.IntegerField(default=25, verbose_name='Процент Берконора'),
        ),
        migrations.AddField(
            model_name='region',
            name='grokcite_proc',
            field=models.IntegerField(default=25, verbose_name='Процент Грокцита'),
        ),
        migrations.AddField(
            model_name='region',
            name='ore_cap',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='Руда: максимум'),
        ),
        migrations.AddField(
            model_name='region',
            name='ore_has',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Руда: в наличии'),
        ),
        migrations.AddField(
            model_name='region',
            name='rnd_mineral',
            field=models.IntegerField(default=25, verbose_name='Процент случайной руды'),
        ),
    ]
