# Generated by Django 3.1.3 on 2022-07-31 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('state', '0038_auto_20220502_1850'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='residency',
            field=models.CharField(choices=[('free', 'Свободная'), ('issue', 'Выдаётся министром')], default='free', max_length=5),
        ),
    ]
