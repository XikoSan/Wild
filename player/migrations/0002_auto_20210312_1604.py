# Generated by Django 3.1.3 on 2021-03-12 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0001_squashed_0007_auto_20210312_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashlog',
            name='activity_txt',
            field=models.CharField(blank=True, choices=[('mine', 'Майнинг'), ('n_str', 'Новый Склад'), ('store', 'Операции со Складом'), ('trans', 'Передача товаров'), ('trade', 'Торговля')], max_length=5, null=True),
        ),
    ]
