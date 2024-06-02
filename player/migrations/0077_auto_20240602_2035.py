# Generated by Django 3.1.3 on 2024-06-02 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0076_auto_20240602_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameevent',
            name='type',
            field=models.CharField(choices=[('hl', 'Хэллоуин'), ('ny', 'Новый год'), ('su', 'Лето')], default='hl', max_length=2, verbose_name='Праздник'),
        ),
    ]
