# Generated by Django 3.1.3 on 2023-11-09 22:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0033_auto_20231109_2110'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='party',
            name='primaries_day',
        ),
        migrations.RemoveField(
            model_name='party',
            name='primaries_time',
        ),
    ]
