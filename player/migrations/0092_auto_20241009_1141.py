# Generated by Django 3.2.18 on 2024-10-09 08:41

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0091_medal_dtime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bonuscode',
            name='color',
            field=models.CharField(blank=True, choices=[('base', 'базовый'), ('red', 'красный'), ('orange', 'оранжевый'), ('yellow', 'желтый'), ('green', 'зелёный'), ('light_blue', 'голубой'), ('dark_blue', 'синий'), ('violet', 'фиолетовый'), ('pink', 'розовый'), ('black', 'чёрный'), ('gold', 'золотой'), ('black_gold', 'чёрно-золотой'), ('wood', 'дерево'), ('dreamflight', 'Dreamflight'), ('android', 'Android tester'), ('hexagon', 'гексагон'), ('standard', 'стандартная схема'), ('green_cam', 'зелёный камуфляж'), ('white_cam', 'белый камуфляж'), ('green_white_cam', 'бело-зелёный камуфляж'), ('blue_cam', 'синий камуфляж'), ('desert_cam', 'песочный камуфляж'), ('corny', 'царь полей'), ('redline', 'красная линия'), ('airball', 'Airball'), ('pobeda', 'пузырьки')], max_length=20, verbose_name='Цвет самолета'),
        ),
        migrations.CreateModel(
            name='TestPointUsage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dtime', models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Время создания записи')),
                ('count', models.IntegerField(default=0, verbose_name='Очки')),
                ('player', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='player.player', verbose_name='Персонаж')),
            ],
            options={
                'verbose_name': 'Траты очков тестирования',
                'verbose_name_plural': 'Траты очков тестирования',
            },
        ),
    ]
