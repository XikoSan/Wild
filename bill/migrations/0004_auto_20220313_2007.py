# Generated by Django 3.1.3 on 2022-03-13 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0003_changeform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changeform',
            name='form',
            field=models.CharField(choices=[('Temporary', 'Временное правительство'), ('Presidential', 'Президентская республика')], default='pres', max_length=15),
        ),
    ]
