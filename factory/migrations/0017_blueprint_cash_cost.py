# Generated by Django 3.1.3 on 2023-09-10 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('factory', '0016_auto_20230910_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='blueprint',
            name='cash_cost',
            field=models.IntegerField(default=1, verbose_name='Затраты Наличных'),
        ),
    ]
