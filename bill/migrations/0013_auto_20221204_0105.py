# Generated by Django 3.1.3 on 2022-12-03 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0012_auto_20221015_2357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseauction',
            name='good',
            field=models.CharField(choices=[('coal', 'Уголь'), ('iron', 'Железо'), ('bauxite', 'Бокситы'), ('wti_oil', 'Нефть WTI'), ('brent_oil', 'Нефть Brent'), ('urals_oil', 'Нефть Urals'), ('gas', 'Бензин'), ('diesel', 'Дизельное топливо'), ('plastic', 'Пластик'), ('steel', 'Сталь'), ('aluminium', 'Алюминий'), ('medical', 'Медикаменты'), ('rifle', 'Автоматы'), ('tank', 'Танки'), ('antitank', 'ПТ-орудия'), ('station', 'Орбитальные орудия'), ('jet', 'Штурмовики'), ('pzrk', 'ПЗРК'), ('ifv', 'БМП'), ('drone', 'БПЛА')], max_length=10, verbose_name='Закупаемый товар'),
        ),
    ]
