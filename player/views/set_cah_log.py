from django.apps import apps


def set_cash_log(player, sum, actvt):
    cash_log_cl = apps.get_model('player.CashLog')
    cash_log = cash_log_cl(player=player, cash=sum, activity_txt=actvt)
    cash_log.save()
