# Generated by Django 3.1.3 on 2022-08-23 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0024_auto_20220820_0023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skilltraining',
            name='skill',
            field=models.CharField(blank=True, choices=[('power', 'Сила'), ('knowledge', 'Знания'), ('endurance', 'Выносливость'), ('Excavation', 'Промышленная экскавация'), ('Finance', 'Подпольное финансирование'), ('Standardization', 'Стандартизация')], max_length=20, null=True, verbose_name='Навык'),
        ),
    ]
