# Generated by Django 3.1.3 on 2021-12-19 19:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('state', '0019_auto_20211219_2221'),
        ('storage', '0027_auto_20211213_2118'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuyAuction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('accept_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted', models.BooleanField(default=False, verbose_name='Удалено')),
                ('treasury_lock', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='treasury_lock', to='state.treasurylock', verbose_name='Блокировка')),
            ],
            options={
                'verbose_name': 'Торговый ордер',
                'verbose_name_plural': 'Торговые ордера',
            },
        ),
    ]
