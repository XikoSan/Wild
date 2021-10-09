# Generated by Django 3.1.3 on 2021-10-06 17:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('region', '0013_auto_20210312_1607'),
        ('state', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Capital',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='capital_placement', to='region.region', verbose_name='Регион размещения')),
                ('state', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cap_state', to='state.state', verbose_name='Государство')),
            ],
            options={
                'verbose_name': 'Столица',
                'verbose_name_plural': 'Столицы',
            },
        ),
    ]
