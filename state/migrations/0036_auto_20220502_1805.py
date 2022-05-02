# Generated by Django 3.1.3 on 2022-05-02 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0019_auto_20210910_2246'),
        ('state', '0035_auto_20220415_0020'),
    ]

    operations = [
        migrations.AddField(
            model_name='deputymandate',
            name='is_president',
            field=models.BooleanField(default=False, verbose_name='Президентский'),
        ),
        migrations.AlterField(
            model_name='deputymandate',
            name='party',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='party.party', verbose_name='Представляет партию'),
        ),
    ]
