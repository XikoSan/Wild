# Generated by Django 3.1.3 on 2024-05-31 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('region', '0053_auto_20240530_0116'),
    ]

    operations = [
        migrations.AddField(
            model_name='plane',
            name='nickname',
            field=models.CharField(default='', max_length=25, verbose_name='Никнейм'),
        ),
        migrations.AddField(
            model_name='plane',
            name='number',
            field=models.IntegerField(default=0, verbose_name='Бортовой номер'),
        ),
        migrations.AlterField(
            model_name='plane',
            name='color',
            field=models.CharField(choices=[('base', 'базовый'), ('red', 'красный'), ('orange', 'оранжевый'), ('yellow', 'желтый'), ('green', 'зелёный'), ('light_blue', 'голубой'), ('dark_blue', 'синий'), ('violet', 'фиолетовый'), ('pink', 'розовый'), ('black', 'чёрный'), ('gold', 'золотой'), ('black_gold', 'чёрно-золотой'), ('wood', 'дерево'), ('dreamflight', 'Dreamflight'), ('green_cam', 'зелёный камуфляж'), ('green_white_cam', 'бело-зелёный камуфляж'), ('blue_cam', 'синий камуфляж'), ('desert_cam', 'песочный камуфляж'), ('airball', 'Airball'), ('pobeda', 'пузырьки')], max_length=20),
        ),
    ]
