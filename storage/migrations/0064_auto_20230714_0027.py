# Generated by Django 3.1.3 on 2023-07-13 21:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0063_auto_20230707_0021'),
    ]

    operations = [
        migrations.AddField(
            model_name='destroy',
            name='count',
            field=models.IntegerField(default=0, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='destroy',
            name='good',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='storage.good', verbose_name='Товар'),
        ),
    ]
