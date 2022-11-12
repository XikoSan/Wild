# Generated by Django 3.1.3 on 2022-11-12 14:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('region', '0025_defences'),
        ('player', '0035_playerregionalexpense'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerregionalexpense',
            name='region',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='expence_region', to='region.region', verbose_name='Регион расходования'),
        ),
    ]
