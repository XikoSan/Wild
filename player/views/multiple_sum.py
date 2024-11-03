import pytz
import datetime
from django.utils import timezone
from math import ceil

def multiple_sum(sum):
    moscow_tz = pytz.timezone('Europe/Moscow')
    start_date = moscow_tz.localize(datetime.datetime(2024, 11, 4, 0, 0))
    # Определяем количество недель с начала
    today = timezone.now()
    weeks_passed = (today - start_date).days // 7 + 1  # Полные недели с начальной даты

    from player.logs.print_log import log
    log(f'weeks_passed: {weeks_passed}')

    # Рассчитываем добавку
    if today >= start_date:
        bonus_percentage = min(weeks_passed * 125, 1000)  # Ограничиваем до 1000%
        log(f'bonus_percentage: {bonus_percentage}')
        sum *= bonus_percentage / 100  # Применяем добавку

    return ceil(sum)