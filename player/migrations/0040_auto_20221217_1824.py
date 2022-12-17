# Generated by Django 3.1.3 on 2022-12-17 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0039_auto_20221217_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventpart',
            name='global_paid_points',
            field=models.IntegerField(default=0, verbose_name='Глобальный оплаченный этап'),
        ),
        migrations.CreateModel(
            name='GlobalPart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(default=0, verbose_name='Очков события')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='player.gameevent', verbose_name='Ивент')),
            ],
            options={
                'verbose_name': 'Общий счет ивента',
                'verbose_name_plural': 'Общие счета ивента',
            },
        ),
    ]
