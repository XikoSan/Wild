# Generated by Django 3.1.3 on 2023-06-27 14:42

from django.db import migrations

def create_neigs(apps, schema_editor):

    neig_list = [
        [21, 9],
        [21, 1],
        [9, 11],
        [9, 1],
        [1, 7],
        [7, 11],
        [7, 11],
        [4, 11],
        [2, 11],
        [4, 2],
        [4, 8],
        [2, 8],
        [6, 8],
        [6, 5],
        [6, 13],
        [5, 13],
        [17, 13],
        [20, 13],
        [17, 5],
        [17, 16],
        [17, 15],
        [17, 20],
        [15, 16],
        [15, 20],
        [16, 20],
    ]

    Neighbours = apps.get_model("region", "Neighbours")
    Region = apps.get_model("region", "Region")

    # обрабатываем только активные регионы
    regions = Region.objects.all()

    for pair in neig_list:
    
        if Region.objects.filter(pk=pair[0]).exists() and Region.objects.filter(pk=pair[1]).exists():
    
            region_1 = Region.objects.get(pk=pair[0])
            region_2 = Region.objects.get(pk=pair[1])
            
            Neighbours.objects.create(
                region_1=region_1,
                region_2=region_2
            )



class Migration(migrations.Migration):

    dependencies = [
        ('region', '0034_auto_20230620_0040'),
    ]

    operations = [
        migrations.RunPython(create_neigs),
    ]
