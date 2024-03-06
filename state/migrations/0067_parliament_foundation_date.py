# Generated by Django 3.1.3 on 2023-11-11 18:31

from django.db import migrations, models
import django.utils.timezone


def set_foundation_date(apps, schema_editor):

    Parliament = apps.get_model("state", "Parliament")
    
    parliaments = Parliament.objects.all()
    
    for parl in parliaments:
    
        parl.foundation_date = parl.state.foundation_date
    
        parl.save()       
            
            
class Migration(migrations.Migration):

    dependencies = [
        ('state', '0066_auto_20231111_2100'),
    ]

    operations = [
        migrations.AddField(
            model_name='parliament',
            name='foundation_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        
        migrations.RunPython(set_foundation_date),
    ]
