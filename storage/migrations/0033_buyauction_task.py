# Generated by Django 3.1.3 on 2022-01-15 21:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_celery_beat', '0015_edit_solarschedule_events_choices'),
        ('storage', '0032_auto_20211220_2103'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyauction',
            name='task',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='django_celery_beat.periodictask'),
        ),
    ]
