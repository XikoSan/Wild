# Generated by Django 3.1.3 on 2023-06-19 21:40

from django.db import migrations
import copy

def region_movement(apps, schema_editor):

    move_dict = {
        21: 25, # Сицилия
        6: 30, # Запад турции
        5: 31, #  центр турции
        13: 32, #  сервер турции
        17: 33, #  восток турции
        20: 34, #  грузия
        16: 36, #  азерб
        15: 35, #  армен
        11: 26, #  зап балк
        2: 29, #  греция
        4: 27, #  центр балк
        8: 28, #  болгария
        9: 24, #  юг италии
        1: 23, #  центр италии
        7: 22, #  центр италии
    }

    Region = apps.get_model("region", "Region")
    MapShape = apps.get_model("region", "MapShape")

    # обрабатываем только активные регионы
    regions = Region.objects.all()

    for region in regions:
        if not region.pk in move_dict.keys():
            continue

        # 1. создаем копию активного региона
        tmp_region = copy.deepcopy(region)

        # 2. Заполняем поля активного региона из нового
        if not Region.with_off.filter(pk=move_dict[region.pk]).exists():
            continue

        new_region = Region.with_off.get(pk=move_dict[region.pk])

        if not MapShape.objects.filter(region=new_region).exists():
            continue

        new_shape = MapShape.objects.get(region=new_region)

        region.region_name = new_region.region_name
        region.on_map_id = new_region.on_map_id

        region.is_north = new_region.is_north
        region.north = new_region.north

        region.is_east = new_region.is_east
        region.east = new_region.east

        region.longitude = new_region.longitude
        region.latitude = new_region.latitude

        new_shape.region = region

        # 3. Заполняем поля нового региона из копии
        old_shape = MapShape.objects.get(region=region)

        new_region.region_name = tmp_region.region_name
        new_region.on_map_id = tmp_region.on_map_id

        new_region.is_north = tmp_region.is_north
        new_region.north = tmp_region.north

        new_region.is_east = tmp_region.is_east
        new_region.east = tmp_region.east

        new_region.longitude = tmp_region.longitude
        new_region.latitude = tmp_region.latitude

        old_shape.region = new_region

        # 4. Сохраняем оба
        region.save()
        new_shape.save()

        new_region.save()
        old_shape.save()




class Migration(migrations.Migration):

    dependencies = [
        ('region', '0033_remove_mapshape_on_map_id'),
    ]

    operations = [
        migrations.RunPython(region_movement),
    ]
