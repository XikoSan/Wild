# Generated by Django 3.1.3 on 2021-10-31 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('state', '0008_treasury_howitzer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='treasury',
            name='howitzer',
        ),
        migrations.AddField(
            model_name='treasury',
            name='ifv',
            field=models.IntegerField(default=0, verbose_name='ifv'),
        ),
    ]
