# Generated by Django 3.1.3 on 2021-02-03 14:12

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0003_auto_20201213_1838'),
        ('storage', '0005_auto_20210203_1753'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dtime', models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Время создания записи')),
                ('total_vol', models.IntegerField(default=0, verbose_name='Всего кубов')),
                ('coal', models.IntegerField(default=0, verbose_name='Уголь')),
                ('coal_vol', models.IntegerField(default=0, verbose_name='Уголь - кубов')),
                ('iron', models.IntegerField(default=0, verbose_name='iron')),
                ('iron_vol', models.IntegerField(default=0, verbose_name='Железо - кубов')),
                ('bauxite', models.IntegerField(default=0, verbose_name='bauxite')),
                ('bauxite_vol', models.IntegerField(default=0, verbose_name='Бокситы - кубов')),
                ('wti_oil', models.IntegerField(default=0, verbose_name='wti_oil')),
                ('wti_oil_vol', models.IntegerField(default=0, verbose_name='wti_oil_cap')),
                ('brent_oil', models.IntegerField(default=0, verbose_name='brent_oil')),
                ('brent_oil_vol', models.IntegerField(default=0, verbose_name='brent_oil_cap')),
                ('urals_oil', models.IntegerField(default=0, verbose_name='urals_oil')),
                ('urals_oil_vol', models.IntegerField(default=0, verbose_name='urals_oil_cap')),
                ('gas', models.IntegerField(default=0, verbose_name='gas')),
                ('gas_vol', models.IntegerField(default=0, verbose_name='gas_cap')),
                ('diesel', models.IntegerField(default=0, verbose_name='diesel')),
                ('diesel_vol', models.IntegerField(default=0, verbose_name='diesel_cap')),
                ('steel', models.IntegerField(default=0, verbose_name='steel')),
                ('steel_vol', models.IntegerField(default=0, verbose_name='steel_cap')),
                ('aluminium', models.IntegerField(default=0, verbose_name='alumunuim')),
                ('aluminium_vol', models.IntegerField(default=0, verbose_name='alumunuim_cap')),
                ('tank', models.IntegerField(default=0, verbose_name='tank')),
                ('tank_vol', models.IntegerField(default=0, verbose_name='Танки- максимум на складе')),
                ('jet', models.IntegerField(default=0, verbose_name='attack_air')),
                ('jet_vol', models.IntegerField(default=0, verbose_name='Штурмовики- максимум на складе')),
                ('station', models.IntegerField(default=0, verbose_name='orb_station')),
                ('station_vol', models.IntegerField(default=0, verbose_name='Орбитальные орудия- максимум на складе')),
                ('pzrk', models.IntegerField(default=0, verbose_name='mpads')),
                ('pzrk_vol', models.IntegerField(default=0, verbose_name='ПЗРК- максимум на складе')),
                ('antitank', models.IntegerField(default=0, verbose_name='antitank')),
                ('antitank_vol', models.IntegerField(default=0, verbose_name='ПТ-пушка- максимум на складе')),
                ('player', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='player.player', verbose_name='Персонаж')),
                ('storage_from', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='storage_from', to='storage.storage', verbose_name='Склад отправки')),
                ('storage_to', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='storage_to', to='storage.storage', verbose_name='Склад отправки')),
            ],
            options={
                'verbose_name': 'Транспорт',
                'verbose_name_plural': 'Транспорты',
            },
        ),
    ]
