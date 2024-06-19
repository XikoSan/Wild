# Generated by Django 3.1.3 on 2024-06-19 18:56

from django.db import migrations
from math import floor


class Migration(migrations.Migration):

    def fix_bp(apps, schema_editor):
        Blueprint = apps.get_model('factory', 'Blueprint')
                    
        blueprints = Blueprint.objects.all()
        
        for blueprint in blueprints:
            
            if blueprint.cash_cost == 8:
                blueprint.cash_cost = 2
                
            elif blueprint.cash_cost == 1:
                blueprint.cash_cost = 1
                
            else:
                blueprint.cash_cost = floor(blueprint.cash_cost / 5)
            
            blueprint.save()

    dependencies = [
        ('factory', '0024_auto_20231031_1500'),
    ]

    operations = [
        migrations.RunPython(fix_bp),
    ]
