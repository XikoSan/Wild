# Generated by Django 3.1.3 on 2022-03-02 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('state', '0026_changetaxes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='changetaxes',
            options={'verbose_name': 'Изменение налогов', 'verbose_name_plural': 'Изменения налогов'},
        ),
        migrations.AddField(
            model_name='changetaxes',
            name='everywhere',
            field=models.BooleanField(default=False, verbose_name='Все регионы'),
        ),
    ]
