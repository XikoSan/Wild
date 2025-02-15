# Generated by Django 3.2.18 on 2024-10-29 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0098_alter_playersettings_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameevent',
            name='type',
            field=models.CharField(choices=[('hl', 'Хэллоуин'), ('ny', 'Новый год'), ('su', 'Лето'), ('av', 'Годовщина')], default='hl', max_length=2, verbose_name='Праздник'),
        ),
        migrations.AlterField(
            model_name='medal',
            name='type',
            field=models.CharField(choices=[('year', 'За год игры в WP'), ('alpha', 'За альфа-тест WP'), ('beta', 'За бета-тест WP'), ('public', 'За открытый тест WP'), ('translator', 'За перевод игры')], default='year', max_length=10),
        ),
    ]
