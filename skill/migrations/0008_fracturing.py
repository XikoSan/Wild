# Generated by Django 3.1.3 on 2023-11-03 18:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0054_auto_20231029_1957'),
        ('skill', '0007_delete_finance'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fracturing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(default=0, verbose_name='Уровень')),
                ('player', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='player.player', verbose_name='Персонаж')),
            ],
            options={
                'verbose_name': 'Гидроразрыв',
                'verbose_name_plural': 'Гидроразрыв',
            },
        ),
    ]
