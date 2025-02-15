# Generated by Django 3.2.18 on 2024-11-17 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0106_auto_20241117_0223'),
        ('article', '0005_commentsblock'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='viewers',
            field=models.ManyToManyField(blank=True, related_name='article_viewers', to='player.Player', verbose_name='Прочитавшие'),
        ),
    ]
