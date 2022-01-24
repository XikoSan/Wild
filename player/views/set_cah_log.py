from django.apps import apps
from datetime import datetime

def set_cash_log(player, sum, actvt, dtime):
    cash_log_cl = apps.get_model('player.CashLog')
    cash_log = cash_log_cl(player=player, cash=sum, activity_txt=actvt, dtime=dtime)
    cash_log.save()
