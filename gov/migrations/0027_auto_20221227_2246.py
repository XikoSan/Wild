# Generated by Django 3.1.3 on 2022-12-27 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gov', '0026_auto_20221103_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ministerright',
            name='right',
            field=models.CharField(choices=[('ChangeCoat', 'Новый герб государства'), ('ChangeTaxes', 'Изменение налогов'), ('ChangeTitle', 'Переименование государства'), ('Construction', 'Строительство'), ('ExploreResources', 'Разведка ресурсов'), ('PurchaseAuction', 'Закупка товаров'), ('ChangeForm', 'Новая форма правления государства'), ('ChangeResidency', 'Новый способ выдачи прописки'), ('StartWar', 'Переименование государства'), ('ForeignRights', 'Министр иностранных дел')], max_length=20),
        ),
    ]
