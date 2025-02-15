# Generated by Django 3.1.3 on 2024-06-02 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0077_auto_20240602_2035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goldlog',
            name='activity_txt',
            field=models.CharField(blank=True, choices=[('reward', 'Бонус за репост'), ('donut', 'VK Donut'), ('mine', 'Майнинг'), ('aumine', 'Авто-майнинг'), ('stckow', 'Процент за авторство'), ('bx_gld', 'Золото из лутбокса'), ('bonus', 'Бонус-код'), ('nick', 'Смена никнейма'), ('avatar', 'Смена аватара'), ('stick', 'Покупка стикеров'), ('energy', 'Энергетики'), ('party', 'Новая партия'), ('ivent', 'Ивент'), ('boxes', 'Покупка лутбокса'), ('edu_01', 'Награда за прокачку характеристики'), ('edu_02', 'Награда за добытое сырьё'), ('edu_03', 'Награда за то, что тяпнул'), ('edu_04', 'Награда за длинную лекцию о Складе'), ('edu_05', 'Награда за изучение карты')], max_length=6, null=True),
        ),
    ]
