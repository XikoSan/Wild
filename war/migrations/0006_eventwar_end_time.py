# Generated by Django 3.1.3 on 2021-10-26 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('war', '0005_auto_20211024_2033'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventwar',
            name='end_time',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Конец войны'),
        ),
    ]
