# Generated by Django 3.1.3 on 2020-11-29 14:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('state', '0001_initial'),
        ('storage', '0002_auto_20201129_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storage',
            name='region',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='placement', to='state.region', verbose_name='Регион размещения'),
        ),
    ]
