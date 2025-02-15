# Generated by Django 3.1.3 on 2021-11-06 11:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0008_auto_20211021_1411'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('war', '0010_warside_antitank'),
    ]

    operations = [
        migrations.AddField(
            model_name='warside',
            name='tank',
            field=models.IntegerField(default=0, verbose_name='Танки'),
        ),
        migrations.CreateModel(
            name='HeavyVehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('side', models.CharField(choices=[('agr', 'Атака'), ('def', 'Оборона')], default='agr', max_length=3)),
                ('deploy', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Ввод в бой')),
                ('destroy', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Уничтожение')),
                ('deleted', models.BooleanField(default=False, verbose_name='Удалено')),
                ('tank', models.IntegerField(default=0, verbose_name='Танки')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('owner', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='war_heavyvehicle', to='player.player', verbose_name='Владелец')),
            ],
            options={
                'verbose_name': 'Отряд тяжелой бронетехники',
                'verbose_name_plural': 'Отряды тяжелой бронетехники',
            },
        ),
    ]
