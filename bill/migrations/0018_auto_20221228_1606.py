# Generated by Django 3.1.3 on 2022-12-28 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0017_auto_20221228_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='startwar',
            name='war_type',
            field=models.CharField(blank=True, choices=[('GroundWar', 'Наземная война')], default=None, max_length=20, null=True, verbose_name='Тип войны'),
        ),
    ]
