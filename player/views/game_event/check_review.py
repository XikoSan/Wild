import pytz
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone
from django.utils import translation
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _
from google_play_scraper import app, reviews_all
from math import ceil
from packaging import version

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.logs.freebie_usage import FreebieUsage
from player.logs.gold_log import GoldLog
from player.logs.prem_log import PremLog
from player.logs.test_log import TestLog
from player.models.rate_reward import RateReward
from player.player import Player
from region.models.plane import Plane
from wild_politics.settings import JResponse


# Проверить отзыв
@login_required(login_url='/')
@check_player
def check_review(request):
    if request.method == "POST":

        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        if FreebieUsage.objects.filter(player=player, type='rate_gold').exists():
            data = {
                'response': pgettext('event', 'Вы уже получили награду'),
                'header': pgettext('shop', 'Получение бонуса'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        # --------------------------------------
        nick = request.POST.get('nick')

        if RateReward.objects.filter(nickname=nick).exists():
            data = {
                'response': pgettext('event', 'За данный отзыв уже получена награда'),
                'header': pgettext('shop', 'Получение бонуса'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        # --------------------------------------

        # Укажите пакет вашего приложения
        package_name = 'com.fogonrog.wildpolitics'

        # Получение отзывов
        review_data = reviews_all(package_name, lang='ru', country='ru')

        # Вывод отзывов
        review = None
        for elem in review_data:
            if nick == elem['userName']:
                review = elem

        if review:
            player.gold += 100 * int(review['score'])
            player.save()

            goldlog = GoldLog(player=player, gold=100 * int(review['score']), activity_txt='bonus')
            goldlog.save()

            usage = FreebieUsage(
                player=player,
                type='rate_gold'
            )
            usage.save()

            RateReward(player=player, nickname=nick).save()

            data = {
                'response': 'ok',
            }
            return JResponse(data)

        else:
            data = {
                'response': pgettext('event', 'Отзыв не найден'),
                'header': pgettext('shop', 'Получение бонуса'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)


    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка метода'),
            'header': pgettext('shop', 'Получение бонуса'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
