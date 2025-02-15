# Generated by Django 3.2.18 on 2024-07-15 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0083_player_fingerprint'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='utm_campaign',
            field=models.CharField(blank=True, max_length=50, verbose_name='utm_campaign'),
        ),
        migrations.AddField(
            model_name='player',
            name='utm_content',
            field=models.CharField(blank=True, max_length=50, verbose_name='utm_content'),
        ),
        migrations.AddField(
            model_name='player',
            name='utm_medium',
            field=models.CharField(blank=True, max_length=50, verbose_name='utm_medium'),
        ),
        migrations.AddField(
            model_name='player',
            name='utm_source',
            field=models.CharField(blank=True, max_length=50, verbose_name='utm_source'),
        ),
        migrations.AddField(
            model_name='player',
            name='utm_term',
            field=models.CharField(blank=True, max_length=50, verbose_name='utm_term'),
        ),
    ]
