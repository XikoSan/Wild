# Generated by Django 3.1.3 on 2021-07-18 19:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0018_auto_20210718_2235'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tradinglog',
            name='accepter_storage',
        ),
        migrations.AddField(
            model_name='tradinglog',
            name='player_storage',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player_storage', to='storage.storage', verbose_name='Склад принявшего оффер'),
        ),
    ]
