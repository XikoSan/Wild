# Generated by Django 3.2.18 on 2024-10-14 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0011_auto_20240922_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='gov',
            field=models.BooleanField(default=False, verbose_name='Гос диалог'),
        ),
    ]
