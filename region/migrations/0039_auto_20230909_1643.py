# Generated by Django 3.1.3 on 2023-09-09 13:43

from django.db import migrations


class Migration(migrations.Migration):

    def return_depletion(apps, schema_editor):
        Region = apps.get_model('region', 'Region')

        for region in Region.with_off.all():

            region.gold_cap += region.gold_depletion
            region.gold_depletion = 0

            region.oil_cap += region.oil_depletion
            region.oil_depletion = 0

            region.ore_cap += region.ore_depletion
            region.ore_depletion = 0

            region.save()

    dependencies = [
        ('region', '0038_merge_20230715_1629'),
    ]

    operations = [
        migrations.RunPython(return_depletion),
    ]
