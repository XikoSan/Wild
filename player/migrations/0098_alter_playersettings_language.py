# Generated by Django 3.2.18 on 2024-10-28 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0097_auto_20241024_1742'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playersettings',
            name='language',
            field=models.CharField(blank=True, choices=[('ru', 'Russian'), ('en', 'English'), ('de', 'Deutsch'), ('be', 'Belarusian'), ('fr', 'French'), ('it', 'Italian'), ('es', 'Spanish'), ('pl', 'Polish'), ('uk', 'Ukrainian'), ('tr', 'Turkish'), ('sr', 'Serbian'), ('id', 'Indonesian'), ('lv', 'Latvian'), ('az', 'Azerbaijani'), ('pt-br', 'Portuguese (Brazil)')], default=None, max_length=7, null=True, verbose_name='Язык в игре'),
        ),
    ]
