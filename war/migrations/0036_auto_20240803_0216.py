# Generated by Django 3.2.18 on 2024-08-02 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('war', '0035_auto_20240715_1540'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='revolution',
            options={'verbose_name': 'Восстание', 'verbose_name_plural': 'Восстания'},
        ),
        migrations.AddField(
            model_name='playerdamage',
            name='hide',
            field=models.BooleanField(default=False, verbose_name='Скрыто'),
        ),
    ]
