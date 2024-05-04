# Generated by Django 3.1.3 on 2024-05-04 16:53

from django.db import migrations

def calculate_new_numbers(a, b, c):
    proportion = 100 / 160  # Определяем пропорцию для новой суммы
    new_a = round(a * proportion / 5) * 5  # Округляем до ближайшего числа, кратного 5
    new_b = round(b * proportion / 5) * 5
    new_c = round(c * proportion / 5) * 5
    
    new_total = new_a + new_b + new_c
    
    if new_total > 100:
        diff = new_total - 100
        max_val = max(new_a, new_b, new_c)
        if max_val == new_a:
            new_a -= diff
        elif max_val == new_b:
            new_b -= diff
        else:
            new_c -= diff
    elif new_total < 100:
        diff = 100 - new_total
        min_val = min(new_a, new_b, new_c)
        if min_val == new_a:
            new_a += diff
        elif min_val == new_b:
            new_b += diff
        else:
            new_c += diff
    
    return new_a, new_b, new_c

def reduce_fossils(apps, schema_editor):

    Region = apps.get_model("region", "Region")
    
    region_u = []
    proportion = 100 / 160
    
    for region in Region.objects.all():
    
        region.gold_cap, region.oil_cap, region.ore_cap = calculate_new_numbers(float(region.gold_cap), float(region.oil_cap), float(region.ore_cap))
        
        region.gold_has = region.gold_cap
        region.oil_has = region.oil_cap
        region.ore_has = region.ore_cap
        
        region_u.append(region)        
    
    Region.objects.bulk_update(
        region_u,
        fields=['gold_has', 'gold_cap',
                'oil_has', 'oil_cap',
                'ore_has', 'ore_cap', ],
        batch_size=len(region_u)
    )


class Migration(migrations.Migration):

    dependencies = [
        ('region', '0048_auto_20240427_2313'),
    ]

    operations = [
        migrations.RunPython(reduce_fossils),
    ]
