# Generated by Django 3.1.3 on 2023-09-03 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0071_tradeoffer_wild_pass'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyauction',
            name='good',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='storage.good', verbose_name='Товар'),
        ),
    ]
