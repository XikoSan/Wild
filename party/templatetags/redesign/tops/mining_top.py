import redis
from django import template
from django.utils.translation import pgettext
import datetime
from player.logs.cash_log import CashLog
from player.player import Player
from player.views.lists.get_thing_page import get_thing_page
from party.party import Party
register = template.Library()
from datetime import timedelta
from django.db.models import Q
from django.db.models import Sum
from metrics.models.daily_ore import DailyOre
from metrics.models.daily_oil import DailyOil

def create_temporary_player_class():
    # класс партии, в котором её место в топе - это поле
    class PartyWithMined(Party):
        pk = 0
        mined = 0
        reward = 0

        class Meta:
            proxy = True
            
    return PartyWithMined



@register.inclusion_tag('player/redesign/lists/uni_list_templatetag.html')
def mining_top(request, player):
    page = request.GET.get('page')

    # берем сумму всех руд за прошедшую неделю
    date_now = datetime.datetime.now()
    date_7d = datetime.datetime.now() - timedelta(days=7)
    week_ore = DailyOre.objects.filter(Q(date__gt=date_7d), Q(date__lt=date_now)).aggregate(total_ore=Sum('ore'))['total_ore']
    # берем сумму всех марок нефти за прошедшую неделю
    week_oil = DailyOil.objects.filter(Q(date__gt=date_7d), Q(date__lt=date_now)).aggregate(total_oil=Sum('oil'))['total_oil']

    r = redis.StrictRedis(host='redis', port=6379, db=0)

    parties = Party.objects.only('pk', 'image', 'title').filter(deleted=False)

    mining_dict = {}

    for party in parties:
        if r.exists("party_mining_" + str(party.pk)):
            mining_dict[party] = int(float(r.get("party_mining_" + str(party.pk))))

    sorted_items = sorted(mining_dict.items(), key=lambda x: x[1], reverse=True)[:10]

    result_list = [(key, value) for key, value in sorted_items]

    parties_with_size = []

    for party_tuple in result_list:
        PartyWithMined = create_temporary_player_class()

        size_party = PartyWithMined(
            title = party_tuple[0].title,
            image = party_tuple[0].image,
        )
        size_party.pk = party_tuple[0].pk,

        size_party.mined = party_tuple[1]

        if week_ore + week_oil == 0:
            size_party.reward = 0
        else:
            size_party.reward = int(10000 * (party_tuple[1] / (week_ore + week_oil)))

        parties_with_size.append(size_party)

    lines = get_thing_page(parties_with_size, page, 10)

    header = {

        'image': {
            'text': '',
            'select_text': pgettext('lists', 'Герб'),
            'visible': 'true'
        },

        'title': {
            'text': pgettext('lists', 'Партия'),
            'select_text': pgettext('lists', 'Партия'),
            'visible': 'true'
        },

        'mined': {
            'text': pgettext('lists', 'Добыто'),
            'select_text': pgettext('lists', 'Добыто'),
            'visible': 'true'
        },

        'reward': {
            'text': '',
            'select_text': pgettext('lists', 'Награда'),
            'visible': 'true'
        },
    }

    return {
        'page_name': pgettext('skill_top', 'Топ добычи'),

        'player': player,

        'header': header,
        'lines': lines,
    }
