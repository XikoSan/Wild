# Generated by Django 3.1.3 on 2021-10-20 16:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0006_auto_20211010_1858'),
        ('state', '0005_auto_20211020_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deputymandate',
            name='player',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='player.player', verbose_name='Депутат'),
        ),
    ]
