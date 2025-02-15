# Generated by Django 3.1.3 on 2024-06-02 20:20

from django.db import migrations

def add_boxes(apps, schema_editor):

    
    Player = apps.get_model("player", "Player")
    Lootbox = apps.get_model("player", "Lootbox")
    
    Lootbox.objects.all().delete()
    
    for player in Player.objects.filter(banned=False):
        
        Lootbox(
            player=player,
            stock=1            
        ).save()


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0084_auto_20240602_2234'),
    ]

    operations = [
        migrations.RunPython(add_boxes),
    ]
