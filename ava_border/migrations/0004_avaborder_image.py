# Generated by Django 3.1.3 on 2022-10-24 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ava_border', '0003_auto_20221025_0037'),
    ]

    operations = [
        migrations.AddField(
            model_name='avaborder',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='img/ava_borders/', verbose_name='Рамка'),
        ),
    ]
