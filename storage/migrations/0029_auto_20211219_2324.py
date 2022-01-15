# Generated by Django 3.1.3 on 2021-12-19 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0028_buyauction'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='buyauction',
            options={'verbose_name': 'Закупочный аукцион', 'verbose_name_plural': 'Закупочные аукционы'},
        ),
        migrations.AddField(
            model_name='buyauction',
            name='good',
            field=models.CharField(choices=[('coal', 'Уголь'), ('iron', 'Железо'), ('bauxite', 'Бокситы'), ('wti_oil', 'Нефть WTI'), ('brent_oil', 'Нефть Brent'), ('urals_oil', 'Нефть Urals'), ('gas', 'Бензин'), ('diesel', 'Дизельное топливо'), ('plastic', 'Пластик'), ('steel', 'Сталь'), ('aluminium', 'Алюминий'), ('medical', 'Койки'), ('rifle', 'Автоматы'), ('tank', 'Танки'), ('antitank', 'ПТ-орудия'), ('station', 'Орбитальные орудия'), ('jet', 'Штурмовики'), ('pzrk', 'ПЗРК'), ('ifv', 'БМП')], default='coal', max_length=10, verbose_name='Товар'),
        ),
    ]
