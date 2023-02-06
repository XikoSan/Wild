# Generated by Django 3.1.3 on 2023-02-06 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gov', '0029_auto_20230120_0119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ministerright',
            name='right',
            field=models.CharField(choices=[('ChangeCoat', 'Новый герб государства'), ('ChangeTaxes', 'Изменение налогов'), ('ChangeTitle', 'Переименование государства'), ('Construction', 'Строительство'), ('ExploreResources', 'Разведка ресурсов'), ('PurchaseAuction', 'Закупка товаров'), ('ChangeForm', 'Новая форма правления государства'), ('ChangeResidency', 'Новый способ выдачи прописки'), ('StartWar', 'Объявление войны'), ('GeologicalSurveys', 'Геологические изыскания'), ('Independence', 'Объявления независимости'), ('ForeignRights', 'Министр иностранных дел')], max_length=20),
        ),
    ]
