# Generated by Django 3.1.3 on 2023-01-19 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('factory', '0008_merge_20230116_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productionlog',
            name='good',
            field=models.CharField(choices=[('cash', 'Наличные'), ('coal', 'Уголь'), ('iron', 'Железо'), ('bauxite', 'Бокситы'), ('wti_oil', 'Нефть WTI'), ('brent_oil', 'Нефть Brent'), ('urals_oil', 'Нефть Urals'), ('gas', 'Бензин'), ('diesel', 'Дизельное топливо'), ('plastic', 'Пластик'), ('steel', 'Сталь'), ('aluminium', 'Алюминий'), ('medical', 'Медикаменты'), ('drilling', 'Буровое оборудование'), ('rifle', 'Автоматы'), ('tank', 'Танки'), ('antitank', 'ПТ-орудия'), ('station', 'Орбитальные орудия'), ('jet', 'Штурмовики'), ('pzrk', 'ПЗРК'), ('ifv', 'БМП'), ('drone', 'БПЛА')], default=None, max_length=20, verbose_name='Товар'),
        ),
    ]
