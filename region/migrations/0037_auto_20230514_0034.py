# Generated by Django 3.1.3 on 2023-05-13 21:34

from django.db import migrations


class Migration(migrations.Migration):

    def create_fossils(apps, schema_editor):
        Region = apps.get_model('region', 'Region')
        Fossils = apps.get_model('region', 'Fossils')
        Good = apps.get_model('storage', 'Good')

        coal = Good.objects.get(name_ru='Уголь')
        iron = Good.objects.get(name_ru='Железо')
        bauxite = Good.objects.get(name_ru='Бокситы')

        for region in Region.with_off.all():
            fossils_c = Fossils(
                region=region,
                good=coal,
                percent=region.coal_proc
            )
            fossils_i = Fossils(
                region=region,
                good=iron,
                percent=region.iron_proc
            )
            fossils_b = Fossils(
                region=region,
                good=bauxite,
                percent=region.bauxite_proc
            )
            fossils_c.save()
            fossils_i.save()
            fossils_b.save()

    dependencies = [
        ('region', '0036_fossils'),
    ]

    operations = [
        migrations.RunPython(create_fossils),
    ]
