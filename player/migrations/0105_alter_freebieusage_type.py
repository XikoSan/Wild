# Generated by Django 3.2.18 on 2024-11-12 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0104_alter_freebieusage_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='freebieusage',
            name='type',
            field=models.CharField(choices=[('gold_500', 'Золото 500'), ('cash_500k', 'Деньги 500k')], default='7_prem', max_length=10),
        ),
    ]
