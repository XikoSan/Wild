# Generated by Django 3.1.3 on 2022-04-04 18:35

from django.db import migrations

def create_hospitals(apps, schema_editor):
    Construction = apps.get_model("bill", "Construction")
    
    Construction.objects.filter(building='med').update(building='Hospital')
   

class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0005_auto_20220404_2109'),
    ]

    operations = [
        migrations.RunPython(create_hospitals),
    ]
