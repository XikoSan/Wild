# Generated by Django 3.1.3 on 2023-03-29 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0049_auto_20230120_0044'),
    ]

    operations = [
        migrations.AddField(
            model_name='destroy',
            name='mines',
            field=models.IntegerField(default=0, verbose_name='Мины'),
        ),
        migrations.AddField(
            model_name='storage',
            name='mines',
            field=models.IntegerField(default=0, verbose_name='Мины'),
        ),
        migrations.AddField(
            model_name='storage',
            name='mines_cap',
            field=models.IntegerField(default=100, verbose_name='Мины - лимит'),
        ),
        migrations.AlterField(
            model_name='buyauction',
            name='good',
            field=models.CharField(choices=[('coal', 'Уголь'), ('iron', 'Железо'), ('bauxite', 'Бокситы'), ('wti_oil', 'Нефть WTI'), ('brent_oil', 'Нефть Brent'), ('urals_oil', 'Нефть Urals'), ('gas', 'Бензин'), ('diesel', 'Дизельное топливо'), ('plastic', 'Пластик'), ('steel', 'Сталь'), ('aluminium', 'Алюминий'), ('medical', 'Медикаменты'), ('drilling', 'Буровые установки'), ('rifle', 'Автоматы'), ('tank', 'Танки'), ('antitank', 'ПТ-орудия'), ('station', 'Орбитальные орудия'), ('jet', 'Штурмовики'), ('pzrk', 'ПЗРК'), ('ifv', 'БМП'), ('mines', 'Мины'), ('drone', 'БПЛА')], default='coal', max_length=10, verbose_name='Товар'),
        ),
        migrations.AlterField(
            model_name='goodlock',
            name='lock_good',
            field=models.CharField(choices=[('coal', 'Уголь'), ('iron', 'Железо'), ('bauxite', 'Бокситы'), ('wti_oil', 'Нефть WTI'), ('brent_oil', 'Нефть Brent'), ('urals_oil', 'Нефть Urals'), ('gas', 'Бензин'), ('diesel', 'Дизельное топливо'), ('plastic', 'Пластик'), ('steel', 'Сталь'), ('aluminium', 'Алюминий'), ('medical', 'Медикаменты'), ('drilling', 'Буровые установки'), ('rifle', 'Автоматы'), ('tank', 'Танки'), ('antitank', 'ПТ-орудия'), ('mines', 'Мины'), ('station', 'Орбитальные орудия'), ('jet', 'Штурмовики'), ('pzrk', 'ПЗРК'), ('ifv', 'БМП'), ('drone', 'Дроны')], default=None, max_length=10),
        ),
        migrations.AlterField(
            model_name='tradeoffer',
            name='good',
            field=models.CharField(choices=[('coal', 'Уголь'), ('iron', 'Железо'), ('bauxite', 'Бокситы'), ('wti_oil', 'Нефть WTI'), ('brent_oil', 'Нефть Brent'), ('urals_oil', 'Нефть Urals'), ('gas', 'Бензин'), ('diesel', 'Дизельное топливо'), ('plastic', 'Пластик'), ('steel', 'Сталь'), ('aluminium', 'Алюминий'), ('medical', 'Медикаменты'), ('drilling', 'Буровые установки'), ('rifle', 'Автоматы'), ('tank', 'Танки'), ('antitank', 'ПТ-орудия'), ('mines', 'Мины'), ('station', 'Орбитальные орудия'), ('jet', 'Штурмовики'), ('pzrk', 'ПЗРК'), ('ifv', 'БМП'), ('drone', 'БПЛА'), ('wild_pass', 'Wild Pass')], default='sell', max_length=10),
        ),
    ]
