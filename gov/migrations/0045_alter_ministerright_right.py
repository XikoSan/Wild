# Generated by Django 3.2.18 on 2024-12-16 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gov', '0044_alter_ministerright_right'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ministerright',
            name='right',
            field=models.CharField(choices=[('ChangeCoat', 'Новый герб государства'), ('ChangeForm', 'Новая форма правления государства'), ('ChangeResidency', 'Новый способ выдачи прописки'), ('ChangeTaxes', 'Изменение налогов'), ('ChangeTitle', 'Переименование государства'), ('Construction', 'Строительство'), ('ExploreResources', 'Разведка ресурсов'), ('Independence', 'Объявление независимости'), ('MartialLaw', 'Военное положение'), ('PurchaseAuction', 'Закупка товаров'), ('StartWar', 'Объявление войны'), ('TransferRegion', 'Передача региона'), ('TransferAccept', 'Принятие региона'), ('TransferResources', 'Передача товаров'), ('ExploreAll', 'Разведка всех регионов'), ('ForeignRights', 'Министр иностранных дел'), ('MiningStats', 'Статистика добычи')], max_length=20),
        ),
    ]
