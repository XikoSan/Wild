# Generated by Django 3.1.3 on 2022-10-21 21:06

from django.db import migrations
from django.utils import timezone
import json

def crontask_remake(apps, schema_editor):

    Parliament = apps.get_model("state", "Parliament")
    ParliamentVoting = apps.get_model("state", "ParliamentVoting")
    
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")
    
    
    parlaments = Parliament.objects.all()
    
    for parl in parlaments:
    
        ParliamentVoting.objects.filter(parliament=parl).delete()
    
        if parl.task is not None:
            task_identificator = parl.task.id
            
            Parliament.objects.select_related('task').filter(pk=parl.id).update(task=None)
            
            PeriodicTask.objects.filter(pk=task_identificator).delete()
        
        foundation_day = parl.state.foundation_date.weekday()

        if foundation_day == 6:
            cron_day = 0
        else:
            cron_day = foundation_day + 1
        
        schedule, created = CrontabSchedule.objects.get_or_create(
                                                            minute=str(parl.state.foundation_date.minute),
                                                            hour=str(parl.state.foundation_date.hour),
                                                            day_of_week=cron_day,
                                                            day_of_month='*',
                                                            month_of_year='*',
                                                           )
                                                           
        task = PeriodicTask(
            name=parl.state.title + ', id парла ' + str(parl.pk),
            task='start_elections',
            crontab=schedule,
            args=json.dumps([parl.id]),
            start_time=timezone.now()
        )
        task.save()
        
        parl.task = task
        
        parl.save()


class Migration(migrations.Migration):

    dependencies = [
        ('state', '0045_auto_20221011_1613'),
    ]

    operations = [
        migrations.RunPython(crontask_remake),
    ]
