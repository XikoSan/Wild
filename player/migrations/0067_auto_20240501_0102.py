# Generated by Django 3.1.3 on 2024-04-30 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0066_auto_20240418_0033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skilltraining',
            name='skill',
            field=models.CharField(blank=True, choices=[('power', 'Сила'), ('knowledge', 'Знания'), ('endurance', 'Выносливость'), ('Excavation', 'Промышленная экскавация'), ('Fracturing', 'Гидроразрыв'), ('Standardization', 'Стандартизация'), ('Biochemistry', 'Биохимия')], max_length=20, null=True, verbose_name='Навык'),
        ),
    ]
