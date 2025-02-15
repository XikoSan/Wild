# Generated by Django 3.1.3 on 2020-12-13 14:30

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('region', '0005_auto_20201211_2032'),
    ]

    operations = [
        migrations.CreateModel(
            name='Party',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30, verbose_name='Название партии')),
                ('type', models.CharField(choices=[('op', 'Открытая'), ('pt', 'Частная')], default='op', max_length=2)),
                ('foundation_date', models.DateTimeField(blank=True, default=datetime.datetime(2000, 1, 1, 0, 0))),
                ('description', models.CharField(blank=True, max_length=300, null=True, verbose_name='Описание партии')),
                ('image', models.ImageField(blank=True, null=True, upload_to='img/party_avatars/', verbose_name='Герб партии')),
                ('members_image_link', models.CharField(blank=True, max_length=150, null=True, verbose_name='Ссылка партийный фон')),
                ('deleted', models.BooleanField(default=False, verbose_name='Удалено')),
                ('region', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='party_region', to='region.region', verbose_name='Регион размещения')),
            ],
            options={
                'verbose_name': 'Партия',
                'verbose_name_plural': 'Партии',
            },
        ),
    ]
