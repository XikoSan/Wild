# Generated by Django 3.1.3 on 2024-04-17 21:33

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0066_auto_20240418_0033'),
        ('state', '0067_parliament_foundation_date'),
        ('django_celery_beat', '0015_edit_solarschedule_events_choices'),
        ('region', '0047_auto_20240418_0026'),
        ('bill', '0035_auto_20240316_1744'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferRegion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('running', models.BooleanField(default=False, verbose_name='Рассматривается')),
                ('type', models.CharField(blank=True, choices=[('ac', 'Принят'), ('rj', 'Отклонён'), ('cn', 'Отменён')], default=None, max_length=2, null=True, verbose_name='Решение')),
                ('cash_cost', models.BigIntegerField(default=0, verbose_name='Наличные')),
                ('voting_start', models.DateTimeField(blank=True, default=datetime.datetime(2000, 1, 1, 0, 0), verbose_name='Время начала рассмотрения')),
                ('voting_end', models.DateTimeField(blank=True, default=datetime.datetime(2000, 1, 1, 0, 0), null=True, verbose_name='Время завершения рассмотрения')),
                ('initiator', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='player.player', verbose_name='Инициатор')),
                ('parliament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='state.parliament', verbose_name='Закон в парламенте')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='region.region', verbose_name='Регион объявления')),
                ('state', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='catcher', to='state.state', verbose_name='Принимает')),
                ('task', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='django_celery_beat.periodictask')),
                ('votes_con', models.ManyToManyField(blank=True, related_name='transferregion_votes_con', to='player.Player', verbose_name='Голоса "против"')),
                ('votes_pro', models.ManyToManyField(blank=True, related_name='transferregion_votes_pro', to='player.Player', verbose_name='Голоса "за"')),
            ],
            options={
                'verbose_name': 'Объявление независимости',
                'verbose_name_plural': 'Объявления независимости',
            },
        ),
    ]
