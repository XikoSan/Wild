import datetime
from datetime import timedelta

from django.utils import timezone


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


# подсчет времени до возможности есст. прироста энергии
def until_increase(player):

    if not player.natural_refill:
        player.natural_refill = timezone.now()

    # узнаем сколько раз по десять минут прошло
    counts = (timezone.now() - player.natural_refill).total_seconds() // 600

    # время в будущем, когда произойдет пополнение
    future_time = player.natural_refill + datetime.timedelta(seconds=(counts+1) * 600)


    if player.energy == 100:
        return 0
    else:
        return abs((future_time - timezone.now()).total_seconds())


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


def format_time(seconds):
    # Создаем объект timedelta с указанным количеством секунд
    delta = datetime.timedelta(seconds=seconds)

    # Используем метод total_seconds() для получения общего количества секунд
    total_seconds = int(delta.total_seconds())

    # Вычисляем количество часов, минут и секунд
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Форматируем время в строку в формате "часы:минуты:секунды"
    time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return time_string