# Generated by Django 3.1.3 on 2024-05-10 19:06

from django.db import migrations
from datetime import datetime, timedelta
from django.utils import timezone

def add_codes(apps, schema_editor):

    bonus_codes = [
        'W246-532-888',
        'W478-286-764',
        'W832-844-895',
        'W987-686-448',
        'W665-962-672',
        'W562-623-924',
        'W499-976-654',
        'W764-949-666',
        'W526-437-562',
        'W838-838-952',
        'W868-346-678',
        'W948-334-583',
        'W793-329-379',
        'W422-346-985',
        'W438-729-547',
        'W464-489-837',
        'W692-888-767',
        'W987-279-442',
        'W526-778-468',
        'W866-746-456'
    ]

    
    BonusCode = apps.get_model("player", "BonusCode")
    
    for text in bonus_codes:
        
        code = BonusCode(
                code=text,
                date=timezone.now() + timedelta(days=365),
                wild_pass=1,
            )
        code.save()
    

class Migration(migrations.Migration):

    dependencies = [
        ('player', '0069_auto_20240506_0103'),
    ]

    operations = [
        migrations.RunPython(add_codes),
    ]


