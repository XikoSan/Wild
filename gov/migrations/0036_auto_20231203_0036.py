# Generated by Django 3.1.3 on 2023-12-02 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gov', '0035_auto_20231112_0035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ministerright',
            name='right',
            field=models.CharField(choices=[('ChangeCoat', 'Новый герб государства'), ('ChangeTaxes', 'Изменение налогов'), ('ChangeTitle', 'Переименование государства'), ('Construction', 'Строительство'), ('ExploreResources', 'Разведка ресурсов'), ('PurchaseAuction', 'Закупка товаров'), ('ChangeForm', 'Новая форма правления государства'), ('ChangeResidency', 'Новый способ выдачи прописки'), ('StartWar', 'Объявление войны'), ('Independence', 'Объявление независимости'), ('ForeignRights', 'Министр иностранных дел'), ('MiningStats', 'Статистика добычи')], max_length=20),
        ),
    ]
