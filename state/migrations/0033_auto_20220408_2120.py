# Generated by Django 3.1.3 on 2022-04-08 18:20

from django.db import migrations

def clear_orbs(apps, schema_editor):
    Treasury = apps.get_model("state", "Treasury")
    
    Treasury.objects.all().update(station=0)

class Migration(migrations.Migration):

    dependencies = [
        ('state', '0032_auto_20220313_2153'),
    ]

    operations = [
      migrations.RunPython(clear_orbs),
    ]
