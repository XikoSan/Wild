# Generated by Django 3.1.3 on 2023-03-30 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0050_auto_20230329_1849'),
    ]

    operations = [
        migrations.AddField(
            model_name='transport',
            name='mines',
            field=models.IntegerField(default=0, verbose_name='Мины'),
        ),
        migrations.AddField(
            model_name='transport',
            name='mines_vol',
            field=models.IntegerField(default=0, verbose_name='Мины - кубов'),
        ),
    ]
