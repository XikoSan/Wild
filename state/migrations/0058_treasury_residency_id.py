# Generated by Django 3.1.3 on 2023-03-11 20:32

from django.db import migrations, models
from django.utils import timezone
import datetime
import json


def residency_run(apps, schema_editor):
    Treasury = apps.get_model("state", "Treasury")
    Parliament = apps.get_model("state", "Parliament")
    ChangeResidency = apps.get_model("bill", "ChangeResidency")

    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    for tres in Treasury.objects.filter(deleted=False):

        if tres.state.residency == 'issue':
            bill = ChangeResidency.objects.filter(
                parliament=Parliament.objects.get(state=tres.state),
                residency='issue',
                type='ac'
            ).order_by('-voting_end').first()

            schedule, created = CrontabSchedule.objects.get_or_create(
                minute=str(bill.voting_end.minute),
                hour='*',
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
            )

            task = PeriodicTask(
                name='прописка, id госа ' + str(tres.state.pk),
                task='residency_pay',
                crontab=schedule,
                args=json.dumps([tres.id]),
                start_time=timezone.now()
            )
            task.save()

            tres.residency_id = task.id
            tres.save()

class Migration(migrations.Migration):

    dependencies = [
        ('state', '0056_auto_20230120_0044'),
    ]

    operations = [
        migrations.AddField(
            model_name='treasury',
            name='residency_id',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='закрытые прописки'),
        ),
        migrations.RunPython(residency_run),
    ]
