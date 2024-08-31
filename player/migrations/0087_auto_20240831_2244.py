# Generated by Django 3.2.18 on 2024-08-31 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0086_alter_skilltraining_skill'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goldlog',
            name='activity_txt',
            field=models.CharField(blank=True, choices=[('reward', 'Бонус за репост'), ('donut', 'VK Donut'), ('mine', 'Майнинг'), ('aumine', 'Авто-майнинг'), ('stckow', 'Процент за авторство'), ('bx_gld', 'Золото из лутбокса'), ('bonus', 'Бонус-код'), ('wpass', 'Активация Wildpass'), ('nick', 'Смена никнейма'), ('avatar', 'Смена аватара'), ('stick', 'Покупка стикеров'), ('energy', 'Энергетики'), ('party', 'Новая партия'), ('ivent', 'Ивент'), ('boxes', 'Покупка лутбокса'), ('rebel', 'Начало восстания'), ('edu_01', 'Награда за прокачку характеристики'), ('edu_02', 'Награда за добытое сырьё'), ('edu_03', 'Награда за то, что тяпнул'), ('edu_04', 'Награда за длинную лекцию о Складе'), ('edu_05', 'Награда за изучение карты')], max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='premlog',
            name='activity_txt',
            field=models.CharField(blank=True, choices=[('buying', 'Покупка'), ('bonus', 'Бонус-код'), ('lootbox', 'Награда из лутбокса'), ('wpass', 'Активация Wildpass')], max_length=7, null=True),
        ),
        migrations.AlterField(
            model_name='wildpasslog',
            name='activity_txt',
            field=models.CharField(blank=True, choices=[('buying', 'Покупка за реал'), ('lootbox', 'Награда из лутбокса'), ('bonus', 'Бонус-код'), ('trading', 'Торговля в игре'), ('using', 'Активация')], max_length=7, null=True),
        ),
    ]
