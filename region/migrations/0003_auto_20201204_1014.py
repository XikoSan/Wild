# Generated by Django 3.1.3 on 2020-12-04 06:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('region', '0002_auto_20201201_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='oil_cap',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='Нефть: максимум'),
        ),
        migrations.AddField(
            model_name='region',
            name='oil_has',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Нефть: в наличии'),
        ),
        migrations.AddField(
            model_name='region',
            name='oil_type',
            field=models.CharField(choices=[('wti_oil', 'Нефть WTI'), ('brent_oil', 'Нефть Brent'), ('urals_oil', 'Нефть Urals')], default='urals_oil', max_length=10),
        ),
    ]
