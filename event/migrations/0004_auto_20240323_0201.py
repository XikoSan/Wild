# Generated by Django 3.1.3 on 2024-03-22 23:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0065_auto_20240305_0121'),
        ('event', '0003_cashevent_casheventpart'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invited', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invited', to='player.player', verbose_name='Приглашённый')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='player.player', verbose_name='Пригласивший')),
            ],
            options={
                'verbose_name': 'Приглашение',
                'verbose_name_plural': 'Приглашения',
            },
        ),
        migrations.DeleteModel(
            name='CashEventPart',
        ),
    ]
