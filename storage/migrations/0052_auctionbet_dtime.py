# Generated by Django 3.1.3 on 2023-06-25 18:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0051_auto_20230330_1048'),
    ]

    operations = [
        migrations.AddField(
            model_name='auctionbet',
            name='dtime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Время создания записи'),
        ),
    ]
