# Generated by Django 3.1.3 on 2022-10-21 22:00

from django.db import migrations
from django.utils import timezone
import json

def crontask_remake(apps, schema_editor):

    ChangeForm = apps.get_model("bill", "ChangeForm")
    Parliament = apps.get_model("state", "Parliament")
    
    President = apps.get_model("gov", "President")
    PresidentialVoting = apps.get_model("gov", "PresidentialVoting")
    
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")
    
    
    presidents = President.objects.all()
    
    for president in presidents:
    
        PresidentialVoting.objects.filter(president=president).delete()
    
        if president.task is not None:
            task_identificator = president.task.id
            
            President.objects.select_related('task').filter(pk=president.id).update(task=None)
            
            PeriodicTask.objects.filter(pk=task_identificator).delete()
        
        law = ChangeForm.objects.filter(parliament=Parliament.objects.get(state=president.state)).first()
        
        foundation_day = law.voting_end.weekday()

        if foundation_day == 6:
            cron_day = 0
        else:
            cron_day = foundation_day + 1
        
        schedule, created = CrontabSchedule.objects.get_or_create(
                                                            minute=str(president.state.foundation_date.minute),
                                                            hour=str(president.state.foundation_date.hour),
                                                            day_of_week=cron_day,
                                                            day_of_month='*',
                                                            month_of_year='*',
                                                           )
                                                           
        task = PeriodicTask(
            name=president.state.title + ', id преза ' + str(president.pk),
            task='start_presidential',
            crontab=schedule,
            args=json.dumps([president.id]),
            start_time=timezone.now()
        )
        task.save()
        
        president.task = task
        
        president.save()
        


class Migration(migrations.Migration):

    dependencies = [
        ('gov', '0019_auto_20221022_0007'),
    ]

    operations = [
        migrations.RunPython(crontask_remake),
    ]
