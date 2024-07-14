# Generated by Django 3.2.18 on 2024-07-14 21:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('region', '0057_auto_20240619_2348'),
        ('django_celery_beat', '0018_improve_crontab_helptext'),
        ('war', '0033_auto_20240626_0022'),
    ]

    operations = [
        migrations.CreateModel(
            name='Revolution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('defence_points', models.BigIntegerField(default=0, verbose_name='Прочность Укрепов')),
                ('running', models.BooleanField(default=False, verbose_name='Идёт война')),
                ('round', models.IntegerField(default=0, verbose_name='Раунд войны')),
                ('start_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Начало войны')),
                ('end_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Конец войны')),
                ('graph', models.TextField(blank=True, default='', null=True, verbose_name='График боя')),
                ('deleted', models.BooleanField(default=False, verbose_name='Удалено')),
                ('hq_points', models.BigIntegerField(default=0, verbose_name='Прочность Штаба')),
                ('agr_region', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='revolution_agr_region', to='region.region', verbose_name='Регион-агрессор')),
                ('def_region', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='revolution_def_region', to='region.region', verbose_name='Регион обороняющихся')),
                ('end_task', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='revolution_end_task', to='django_celery_beat.periodictask')),
                ('task', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='revolution_round_task', to='django_celery_beat.periodictask')),
            ],
            options={
                'verbose_name': 'Наземная война',
                'verbose_name_plural': 'Наземные войны',
            },
        ),
    ]
