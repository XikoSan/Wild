# Generated by Django 3.1.3 on 2024-06-02 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('region', '0055_auto_20240601_0045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plane',
            name='plane',
            field=models.CharField(choices=[('nagger', 'Nagger'), ('pretender', 'Pretender'), ('trickster', 'Trickster'), ('smuggler', 'Smuggler'), ('chaser', 'Chaser'), ('reaper', 'Reaper'), ('cheater', 'Cheater'), ('carrier', 'Carrier'), ('observer', 'Observer'), ('striker', 'Striker'), ('demolisher', 'Demolisher'), ('sprinter', 'Sprinter'), ('harrier', 'Harrier'), ('sailor', 'Sailor'), ('hammer', 'Hammer'), ('beluzzo', 'Диск Белуццо')], max_length=10),
        ),
    ]
