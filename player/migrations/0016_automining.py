# Generated by Django 3.1.3 on 2022-04-16 22:16

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0015_player_premium'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutoMining',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dtime', models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Время создания записи')),
                ('resource', models.CharField(blank=True, choices=[('gold', 'Золото'), ('oil', 'Нефть'), ('ore', 'Руда')], max_length=4, null=True, verbose_name='Ресурс')),
                ('player', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='player.player', verbose_name='Персонаж')),
            ],
            options={
                'verbose_name': 'Автоматический сбор',
                'verbose_name_plural': 'Автоматически собираемые ресурсы',
            },
        ),
    ]
