# Generated by Django 3.1.3 on 2022-07-27 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gov', '0011_auto_20220702_1852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ministerright',
            name='right',
            field=models.CharField(choices=[('ChangeCoat', 'Новый герб государства'), ('ChangeTaxes', 'Изменение налогов'), ('ChangeTitle', 'Переименование государства'), ('Construction', 'Строительство'), ('ExploreResources', 'Разведка ресурсов'), ('PurchaseAuction', 'Закупка товаров'), ('ChangeForm', 'Новая форма правления государства')], max_length=20),
        ),
    ]
