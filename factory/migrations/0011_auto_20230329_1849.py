# Generated by Django 3.1.3 on 2023-03-29 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('factory', '0010_auto_20230120_0044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productionlog',
            name='good',
            field=models.CharField(choices=[('cash', 'Наличные'), ('coal', 'Уголь'), ('iron', 'Железо'), ('bauxite', 'Бокситы'), ('wti_oil', 'Нефть WTI'), ('brent_oil', 'Нефть Brent'), ('urals_oil', 'Нефть Urals'), ('gas', 'Бензин'), ('diesel', 'Дизельное топливо'), ('plastic', 'Пластик'), ('steel', 'Сталь'), ('aluminium', 'Алюминий'), ('medical', 'Медикаменты'), ('drilling', 'Буровые установки'), ('rifle', 'Автоматы'), ('tank', 'Танки'), ('antitank', 'ПТ-орудия'), ('station', 'Орбитальные орудия'), ('jet', 'Штурмовики'), ('pzrk', 'ПЗРК'), ('ifv', 'БМП'), ('mines', 'Мины'), ('drone', 'БПЛА')], default=None, max_length=20, verbose_name='Товар'),
        ),
    ]
