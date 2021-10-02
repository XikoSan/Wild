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


# универсальный подсчитыватель времени в секундах до конца процесса
# object - объект, для которого рассчитывается интервал времени
# start_fname - имя поля объекта, в котором лежит DateTime начала процесса
# end_fname - имя поля объекта, в котором лежит DateTime окончания процесса (необязательно)
# delay_in_sec - разница между datetime начала и окончания прцоесса (если не задано выше) (необязательно)
def interval_in_seconds(object, start_fname, end_fname, delay_in_sec):
    # время сейчас
    cur_time = timezone.now()
    # время, когда процесс закончится
    if end_fname:
        end_time = getattr(object, end_fname)
    elif start_fname and delay_in_sec:
        end_time = getattr(object, start_fname) + timedelta(seconds=delay_in_sec)
    else:
        return 0

    if end_time > cur_time:
        # узнаем, сколько осталось до конца
        dif = int((end_time - cur_time).total_seconds())
        return dif
    else:
        return 0
