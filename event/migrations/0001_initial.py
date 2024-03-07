# Generated by Django 3.1.3 on 2024-02-04 20:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('player', '0061_auto_20240130_2230'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('running', models.BooleanField(default=False, verbose_name='Включен')),
                ('title', models.CharField(max_length=30, verbose_name='Никнейм')),
                ('event_start', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Время начала')),
                ('event_end', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Время завершения')),
            ],
            options={
                'verbose_name': 'Ивент активности',
                'verbose_name_plural': 'Ивенты активности',
            },
        ),
        migrations.CreateModel(
            name='ActivityGlobalPart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(default=0, verbose_name='Очков события')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event.activityevent', verbose_name='Ивент')),
            ],
            options={
                'verbose_name': 'Общий счет ивента активности',
                'verbose_name_plural': 'Общие счета ивентов активности',
            },
        ),
        migrations.CreateModel(
            name='ActivityEventPart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(default=0, verbose_name='Очков события')),
                ('paid_points', models.IntegerField(default=0, verbose_name='Последний оплаченный этап')),
                ('global_paid_points', models.IntegerField(default=0, verbose_name='Глобальный оплаченный этап')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event.activityevent', verbose_name='Ивент')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='player.player', verbose_name='Игрок')),
            ],
            options={
                'verbose_name': 'Участник ивента активностей',
                'verbose_name_plural': 'Участники ивента активностей',
            },
        ),
    ]
