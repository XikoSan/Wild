# Generated by Django 3.1.3 on 2022-10-07 09:28

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
        
        cron_day = parl.state.foundation_date.weekday() + 1
        
        schedule, created = CrontabSchedule.objects.get_or_create(
                                                            minute=str(timezone.now().now().minute),
                                                            hour=str(timezone.now().now().hour),
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
        ('state', '0042_auto_20220828_1627'),
    ]

    operations = [
        migrations.RunPython(crontask_remake),
    ]
