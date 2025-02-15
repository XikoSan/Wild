# Generated by Django 3.1.3 on 2022-07-20 19:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0021_auto_20220510_1903'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color_back', models.CharField(default='28353E', max_length=6)),
                ('color_block', models.CharField(default='284E64', max_length=6)),
                ('color_text', models.CharField(default='FFFFFF', max_length=6)),
                ('color_acct', models.CharField(default='EB9929', max_length=6)),
                ('player', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='character_id', to='player.player', verbose_name='Игрок')),
            ],
            options={
                'verbose_name': 'Настройки игрока',
                'verbose_name_plural': 'Настройки игрока',
            },
        ),
    ]
