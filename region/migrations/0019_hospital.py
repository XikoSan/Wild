# Generated by Django 3.1.3 on 2022-04-02 11:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('region', '0018_region_med_lvl'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(default=0, verbose_name='Уровень здания')),
                ('top', models.IntegerField(default=1, verbose_name='Рейтинг здания')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='region.region', verbose_name='Регион строительства')),
            ],
            options={
                'verbose_name': 'Больница',
                'verbose_name_plural': 'Больницы',
            },
        ),
    ]
