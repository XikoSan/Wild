# Generated by Django 3.1.3 on 2023-07-21 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0070_auto_20230722_0040'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradeoffer',
            name='wild_pass',
            field=models.BooleanField(default=False, verbose_name='Wild Pass'),
        ),
    ]
