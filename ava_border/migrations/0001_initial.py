# Generated by Django 3.1.3 on 2022-10-22 18:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('player', '0030_auto_20221018_2118'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvaBorder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание')),
                ('image', models.ImageField(upload_to='img/stickers/', verbose_name='Рамка')),
                ('price', models.IntegerField(default=1000, verbose_name='Цена')),
                ('deleted', models.BooleanField(default=False, verbose_name='Удалено')),
            ],
            options={
                'verbose_name': 'Рамка аватара',
                'verbose_name_plural': 'Рамки аватара',
            },
        ),
        migrations.CreateModel(
            name='AvaBorderOwnership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('in_use', models.BooleanField(default=False, verbose_name='Используется')),
                ('border', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ava_border.avaborder', verbose_name='Рамка')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='player.player', verbose_name='Игрок')),
            ],
            options={
                'verbose_name': 'Владелец рамки',
                'verbose_name_plural': 'Владельцы рамок',
            },
        ),
    ]
