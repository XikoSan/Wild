# Generated by Django 3.1.3 on 2023-10-01 21:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0051_merge_20230715_1629'),
        ('chat', '0007_auto_20220510_1830'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMembers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Участник чата',
                'verbose_name_plural': 'Участники чата',
            },
        ),
        migrations.CreateModel(
            name='MessageBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('messages', models.TextField()),
            ],
            options={
                'verbose_name': 'Блок сообщений',
                'verbose_name_plural': 'Блоки сообщений',
            },
        ),
        migrations.AlterModelOptions(
            name='chat',
            options={'verbose_name': 'Чат', 'verbose_name_plural': 'Чаты'},
        ),
        migrations.RemoveField(
            model_name='chat',
            name='chat_id',
        ),
        migrations.RemoveField(
            model_name='chat',
            name='messages',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
        migrations.AddField(
            model_name='messageblock',
            name='chat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.chat'),
        ),
        migrations.AddField(
            model_name='chatmembers',
            name='chat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.chat'),
        ),
        migrations.AddField(
            model_name='chatmembers',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='player.player'),
        ),
    ]
