# Generated by Django 3.1.3 on 2022-11-02 12:09

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
                
        law = ChangeForm.objects.filter(parliament=Parliament.objects.get(state=president.state)).first()
    
        foundation_day = law.voting_end.weekday()

        if foundation_day == 6:
            cron_day = 0
        else:
            cron_day = foundation_day + 1
    
        if president.task is not None:                
            
            if president.task.crontab.day_of_week != cron_day:
                
                schedule = CrontabSchedule.objects.create(
                                                        minute=str(law.voting_end.minute),
                                                        hour=str(law.voting_end.hour),
                                                        day_of_week=cron_day,
                                                        day_of_month='*',
                                                        month_of_year='*',
                                                       )
                                                                   
                president.task.crontab = schedule
                
                president.task.save()
                
        
        if PresidentialVoting.objects.filter(president=president, task__isnull=False).exists():
        
            if cron_day == 6:
                cron_day = 0                
            else:
                cron_day += 1
            
            voting = PresidentialVoting.objects.get(president=president, task__isnull=False)
            
            if voting.task is not None:   
            
                if voting.task.crontab.day_of_week != cron_day:
                
                    schedule = CrontabSchedule.objects.create(
                                                            minute=str(law.voting_end.minute),
                                                            hour=str(law.voting_end.hour),
                                                            day_of_week=cron_day,
                                                            day_of_month='*',
                                                            month_of_year='*',
                                                           )
                                                                       
                    voting.task.crontab = schedule
                    
                    voting.task.save()
            



class Migration(migrations.Migration):

    dependencies = [
        ('gov', '0022_auto_20221102_1243'),
    ]

    operations = [
        migrations.RunPython(crontask_remake),
    ]
