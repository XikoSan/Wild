# Generated by Django 3.1.3 on 2022-07-02 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gov', '0010_remove_ministerright_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ministerright',
            name='right',
            field=models.CharField(choices=[('ChangeCoat', 'Новый герб государства'), ('ChangeTaxes', 'Изменение налогов'), ('ChangeTitle', 'Переименование государства'), ('Construction', 'Строительство'), ('ExploreResources', 'Разведка ресурсов'), ('PurchaseAuction', 'Закупка товаров'), ('ChangeForm', 'Новая форма правления государства'), ('EnergyRights', 'Министр энергетики')], max_length=20),
        ),
    ]
