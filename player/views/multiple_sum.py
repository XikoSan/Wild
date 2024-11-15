import pytz
import datetime
from django.utils import timezone
from math import ceil

def multiple_sum(sum, lag=0):
    moscow_tz = pytz.timezone('Europe/Moscow')
    start_date = moscow_tz.localize(datetime.datetime(2024, 11, 4, 0, 0))
    # Определяем количество недель с начала
    today = timezone.now()
    weeks_passed = (today - start_date).days // 7 + 1 + lag  # Полные недели с начальной даты. Если задан lag, то рост (выплат) будет сильнее

    # Рассчитываем добавку
    if today >= start_date:
        bonus_percentage = min(weeks_passed * 125, 1000)  # Ограничиваем до 1000%
        sum *= bonus_percentage / 100  # Применяем добавку

    return ceil(sum)