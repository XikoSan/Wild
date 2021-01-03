from django.utils import timezone
from datetime import datetime, timedelta


# подсчет времени до возможности пополнить энергию
def until_recharge(player):
    # время сейчас
    cur_time = timezone.now()
    # время, когда можно перезаряжаться
    end_time = player.last_refill

    if end_time > cur_time:
        # узнаем, сколько осталось до конца перезарядки
        dif = (end_time - cur_time).seconds
        return dif
    else:
        return 0
