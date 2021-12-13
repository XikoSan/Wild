# Generated by Django 3.1.3 on 2021-12-13 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0026_auto_20211213_2036'),
    ]

    operations = [
        migrations.AddField(
            model_name='destroy',
            name='plastic',
            field=models.IntegerField(default=0, verbose_name='plastic'),
        ),
        migrations.AddField(
            model_name='productionlog',
            name='plastic',
            field=models.IntegerField(default=0, verbose_name='plastic'),
        ),
        migrations.AddField(
            model_name='storage',
            name='plastic',
            field=models.IntegerField(default=0, verbose_name='plastic'),
        ),
        migrations.AddField(
            model_name='storage',
            name='plastic_cap',
            field=models.IntegerField(default=10000, verbose_name='plastic_cap'),
        ),
        migrations.AddField(
            model_name='transport',
            name='plastic',
            field=models.IntegerField(default=0, verbose_name='Пластик'),
        ),
        migrations.AddField(
            model_name='transport',
            name='plastic_vol',
            field=models.IntegerField(default=0, verbose_name='Пластик - кубов'),
        ),
        migrations.AlterField(
            model_name='goodlock',
            name='lock_good',
            field=models.CharField(choices=[('coal', 'Уголь'), ('iron', 'Железо'), ('bauxite', 'Бокситы'), ('wti_oil', 'Нефть WTI'), ('brent_oil', 'Нефть Brent'), ('urals_oil', 'Нефть Urals'), ('gas', 'Бензин'), ('diesel', 'Дизельное топливо'), ('plastic', 'Пластик'), ('steel', 'Сталь'), ('aluminium', 'Алюминий'), ('medical', 'Койки'), ('rifle', 'Автоматы'), ('tank', 'Танки'), ('antitank', 'ПТ-орудия'), ('station', 'Орбитальные орудия'), ('jet', 'Штурмовики'), ('pzrk', 'ПЗРК'), ('ifv', 'БМП')], default=None, max_length=10),
        ),
        migrations.AlterField(
            model_name='tradeoffer',
            name='good',
            field=models.CharField(choices=[('coal', 'Уголь'), ('iron', 'Железо'), ('bauxite', 'Бокситы'), ('wti_oil', 'Нефть WTI'), ('brent_oil', 'Нефть Brent'), ('urals_oil', 'Нефть Urals'), ('gas', 'Бензин'), ('diesel', 'Дизельное топливо'), ('plastic', 'Пластик'), ('steel', 'Сталь'), ('aluminium', 'Алюминий'), ('medical', 'Койки'), ('rifle', 'Автоматы'), ('tank', 'Танки'), ('antitank', 'ПТ-орудия'), ('station', 'Орбитальные орудия'), ('jet', 'Штурмовики'), ('pzrk', 'ПЗРК'), ('ifv', 'БМП')], default='sell', max_length=10),
        ),
    ]
