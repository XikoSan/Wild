# Generated by Django 3.1.3 on 2020-11-30 14:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('region', '0001_initial'),
        ('player', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.BigIntegerField(default=0, verbose_name='storage_cash')),
                ('anohor', models.IntegerField(default=0, verbose_name='anohor')),
                ('anohor_cap', models.IntegerField(default=100000, verbose_name='anohor_cap')),
                ('berkonor', models.IntegerField(default=0, verbose_name='berkonor')),
                ('berkonor_cap', models.IntegerField(default=100000, verbose_name='berkonor_cap')),
                ('grokcite', models.IntegerField(default=0, verbose_name='grokcite')),
                ('grokcite_cap', models.IntegerField(default=100000, verbose_name='grokcite_cap')),
                ('wti_oil', models.IntegerField(default=0, verbose_name='wti_oil')),
                ('wti_oil_cap', models.IntegerField(default=100000, verbose_name='wti_oil_cap')),
                ('brent_oil', models.IntegerField(default=0, verbose_name='brent_oil')),
                ('brent_oil_cap', models.IntegerField(default=100000, verbose_name='brent_oil_cap')),
                ('urals_oil', models.IntegerField(default=0, verbose_name='urals_oil')),
                ('urals_oil_cap', models.IntegerField(default=100000, verbose_name='urals_oil_cap')),
                ('gas', models.IntegerField(default=0, verbose_name='gas')),
                ('gas_cap', models.IntegerField(default=10000, verbose_name='gas_cap')),
                ('diesel', models.IntegerField(default=0, verbose_name='diesel')),
                ('diesel_cap', models.IntegerField(default=10000, verbose_name='diesel_cap')),
                ('steel', models.IntegerField(default=0, verbose_name='steel')),
                ('steel_cap', models.IntegerField(default=10000, verbose_name='steel_cap')),
                ('alumunuim', models.IntegerField(default=0, verbose_name='alumunuim')),
                ('alumunuim_cap', models.IntegerField(default=10000, verbose_name='alumunuim_cap')),
                ('tank', models.IntegerField(default=0, verbose_name='tank')),
                ('tank_cap', models.IntegerField(default=1000, verbose_name='Танки- максимум на складе')),
                ('jet', models.IntegerField(default=0, verbose_name='attack_air')),
                ('jet_cap', models.IntegerField(default=1000, verbose_name='Штурмовики- максимум на складе')),
                ('station', models.IntegerField(default=0, verbose_name='orb_station')),
                ('station_cap', models.IntegerField(default=10, verbose_name='Орбитальные орудия- максимум на складе')),
                ('pzrk', models.IntegerField(default=0, verbose_name='mpads')),
                ('pzrk_cap', models.IntegerField(default=1000, verbose_name='ПЗРК- максимум на складе')),
                ('antitank', models.IntegerField(default=0, verbose_name='antitank')),
                ('antitank_cap', models.IntegerField(default=1000, verbose_name='ПТ-пушка- максимум на складе')),
                ('owner', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to='player.player', verbose_name='Владелец')),
                ('region', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='placement', to='region.region', verbose_name='Регион размещения')),
            ],
            options={
                'verbose_name': 'Склад',
                'verbose_name_plural': 'Склады',
            },
        ),
    ]
