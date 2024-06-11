# coding=utf-8
import json
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import pgettext
from django.utils.translation import ugettext

from player.decorators.player import check_player
from player.logs.auto_mining import AutoMining
from player.player import Player
from region.models.neighbours import Neighbours
from region.models.region import Region
from storage.models.storage import Storage
from wild_politics.settings import JResponse


# сформировать рейтинг регионов по онлайну и застройке
def form_development_top():
    pass
    # получить среднее значение инедксов застройки для всех регионов
    # сформировать упорядоченный список этих регионов

    # получить онлайн для всех регионов
    # сформировать упорядоченный список этих регионов

    # сформировать общий список, где позиция определяется по количеству очков у региона. Первое место - максимум очков

