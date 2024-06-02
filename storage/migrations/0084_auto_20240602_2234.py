# Generated by Django 3.1.3 on 2024-06-02 19:34

from django.db import migrations

def clear_planes(apps, schema_editor):

    
    Plane = apps.get_model("region", "Plane")
    
    Plane.objects.exclude(color='dreamflight').delete()
    

class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0083_auto_20240602_1907'),
    ]

    operations = [
        migrations.RunPython(clear_planes),
    ]
