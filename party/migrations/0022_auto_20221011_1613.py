# Generated by Django 3.1.3 on 2022-10-11 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0021_auto_20221008_2335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='primaries',
            name='running',
            field=models.BooleanField(default=True, verbose_name='Идут прямо сейчас'),
        ),
    ]
