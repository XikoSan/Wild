# Generated by Django 3.1.3 on 2022-04-15 20:47

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0013_goldlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='endurance',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='player',
            name='knowledge',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='player',
            name='power',
            field=models.IntegerField(default=1),
        ),
        migrations.CreateModel(
            name='SkillTraining',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dtime', models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Время создания записи')),
                ('skill', models.CharField(blank=True, choices=[('power', 'Сила'), ('knowledge', 'Знания'), ('endurance', 'Выносливость')], max_length=20, null=True, verbose_name='Навык')),
                ('end_dtime', models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Время завершения')),
                ('player', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='player.player', verbose_name='Персонаж')),
            ],
            options={
                'verbose_name': 'Изучаемый навык',
                'verbose_name_plural': 'Изучаемые навыки',
            },
        ),
    ]
