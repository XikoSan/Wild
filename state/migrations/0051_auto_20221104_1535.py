# Generated by Django 3.1.3 on 2022-11-04 12:35

from django.db import migrations

from state.tasks import start_elections


def crontask_start(apps, schema_editor):
    
    start_elections(14)

class Migration(migrations.Migration):

    dependencies = [
        ('state', '0050_auto_20221102_1525'),
    ]

    operations = [
        migrations.RunPython(crontask_start),
    ]
