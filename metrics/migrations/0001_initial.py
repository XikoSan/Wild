# Generated by Django 3.1.3 on 2023-03-08 20:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DailyCash',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('cash', models.BigIntegerField(default=0, verbose_name='Добыто денег')),
            ],
            options={
                'verbose_name': 'Заработок за день',
                'verbose_name_plural': 'Заработок за день',
            },
        ),
    ]
