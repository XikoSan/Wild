# Generated by Django 3.1.3 on 2021-02-28 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0009_destroy'),
    ]

    operations = [
        migrations.AddField(
            model_name='transport',
            name='delivery_value',
            field=models.BigIntegerField(default=0, verbose_name='Стоимость доставки'),
        ),
    ]
