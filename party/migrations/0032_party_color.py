# Generated by Django 3.1.3 on 2023-06-28 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0031_auto_20221104_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='color',
            field=models.CharField(default='xxxxxx', max_length=6),
        ),
    ]
