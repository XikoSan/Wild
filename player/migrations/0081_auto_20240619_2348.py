# Generated by Django 3.1.3 on 2024-06-19 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0080_auto_20240602_2240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bonuscode',
            name='color',
            field=models.CharField(blank=True, choices=[('base', 'базовый'), ('red', 'красный'), ('orange', 'оранжевый'), ('yellow', 'желтый'), ('green', 'зелёный'), ('light_blue', 'голубой'), ('dark_blue', 'синий'), ('violet', 'фиолетовый'), ('pink', 'розовый'), ('black', 'чёрный'), ('gold', 'золотой'), ('black_gold', 'чёрно-золотой'), ('wood', 'дерево'), ('dreamflight', 'Dreamflight'), ('hexagon', 'гексагон'), ('standard', 'стандартная схема'), ('green_cam', 'зелёный камуфляж'), ('white_cam', 'белый камуфляж'), ('green_white_cam', 'бело-зелёный камуфляж'), ('blue_cam', 'синий камуфляж'), ('desert_cam', 'песочный камуфляж'), ('corny', 'царь полей'), ('redline', 'красная линия'), ('airball', 'Airball'), ('pobeda', 'пузырьки')], max_length=20, verbose_name='Цвет самолета'),
        ),
    ]
