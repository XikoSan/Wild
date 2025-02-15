# Generated by Django 3.1.3 on 2024-03-01 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0061_auto_20240130_2230'),
        ('article', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='votes_con',
            field=models.ManyToManyField(blank=True, related_name='article_votes_con', to='player.Player', verbose_name='Голоса "против"'),
        ),
        migrations.AddField(
            model_name='article',
            name='votes_pro',
            field=models.ManyToManyField(blank=True, related_name='article_votes_pro', to='player.Player', verbose_name='Голоса "за"'),
        ),
    ]
