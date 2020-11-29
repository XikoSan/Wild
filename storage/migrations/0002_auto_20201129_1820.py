# Generated by Django 3.1.3 on 2020-11-29 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storage',
            name='oil',
        ),
        migrations.RemoveField(
            model_name='storage',
            name='oil_cap',
        ),
        migrations.RemoveField(
            model_name='storage',
            name='ore',
        ),
        migrations.RemoveField(
            model_name='storage',
            name='ore_cap',
        ),
        migrations.AddField(
            model_name='storage',
            name='alumunuim',
            field=models.IntegerField(default=0, verbose_name='alumunuim'),
        ),
        migrations.AddField(
            model_name='storage',
            name='alumunuim_cap',
            field=models.IntegerField(default=10000, verbose_name='alumunuim_cap'),
        ),
        migrations.AddField(
            model_name='storage',
            name='anohor',
            field=models.IntegerField(default=0, verbose_name='anohor'),
        ),
        migrations.AddField(
            model_name='storage',
            name='anohor_cap',
            field=models.IntegerField(default=100000, verbose_name='anohor_cap'),
        ),
        migrations.AddField(
            model_name='storage',
            name='berkonor',
            field=models.IntegerField(default=0, verbose_name='berkonor'),
        ),
        migrations.AddField(
            model_name='storage',
            name='berkonor_cap',
            field=models.IntegerField(default=100000, verbose_name='berkonor_cap'),
        ),
        migrations.AddField(
            model_name='storage',
            name='brent_oil',
            field=models.IntegerField(default=0, verbose_name='brent_oil'),
        ),
        migrations.AddField(
            model_name='storage',
            name='brent_oil_cap',
            field=models.IntegerField(default=100000, verbose_name='brent_oil_cap'),
        ),
        migrations.AddField(
            model_name='storage',
            name='diesel',
            field=models.IntegerField(default=0, verbose_name='diesel'),
        ),
        migrations.AddField(
            model_name='storage',
            name='diesel_cap',
            field=models.IntegerField(default=10000, verbose_name='diesel_cap'),
        ),
        migrations.AddField(
            model_name='storage',
            name='grokcite',
            field=models.IntegerField(default=0, verbose_name='grokcite'),
        ),
        migrations.AddField(
            model_name='storage',
            name='grokcite_cap',
            field=models.IntegerField(default=100000, verbose_name='grokcite_cap'),
        ),
        migrations.AddField(
            model_name='storage',
            name='urals_oil',
            field=models.IntegerField(default=0, verbose_name='urals_oil'),
        ),
        migrations.AddField(
            model_name='storage',
            name='urals_oil_cap',
            field=models.IntegerField(default=100000, verbose_name='urals_oil_cap'),
        ),
        migrations.AddField(
            model_name='storage',
            name='wti_oil',
            field=models.IntegerField(default=0, verbose_name='wti_oil'),
        ),
        migrations.AddField(
            model_name='storage',
            name='wti_oil_cap',
            field=models.IntegerField(default=100000, verbose_name='wti_oil_cap'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='gas_cap',
            field=models.IntegerField(default=10000, verbose_name='gas_cap'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='steel_cap',
            field=models.IntegerField(default=10000, verbose_name='steel_cap'),
        ),
    ]
