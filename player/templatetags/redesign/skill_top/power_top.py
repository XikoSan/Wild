from django import template
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _
from player.logs.cash_log import CashLog
from player.views.lists.get_thing_page import get_thing_page
from player.player import Player

register = template.Library()

def create_temporary_player_class():
    # класс игрока, с местом в рейтинге
    class PPlayerWithTop(Player):
        pk = 0
        top = 0

        class Meta:
            proxy = True

    return PPlayerWithTop



@register.inclusion_tag('player/redesign/lists/uni_list_templatetag.html')
def power_top(request, player):
    page = request.GET.get('page')
    logs = Player.objects.only('pk', 'image', 'nickname', 'power').all().order_by('-power')[:10]

    players = []
    index = 1

    for line in logs:

        PPlayerWithTop = create_temporary_player_class()

        char = PPlayerWithTop(
            nickname = line.nickname,
        )
        char.top = index

        char.pk = line.pk
        char.image = line.image
        char.power = line.power

        players.append(char)
        index += 1

    lines = get_thing_page(players, page, 10)

    header = {

        'top': {
            'text': pgettext('lists', 'Место'),
            'select_text': pgettext('lists', 'Место'),
            'visible': 'true'
        },

        'image': {
            'text': '',
            'select_text': pgettext('lists', 'Аватар'),
            'visible': 'true'
        },

        'nickname': {
            'text': pgettext('lists', 'Никнейм'),
            'select_text': pgettext('lists', 'Никнейм'),
            'visible': 'true'
        },

        'power': {
            'text': pgettext('lists', 'Сила'),
            'select_text': pgettext('lists', 'Сила'),
            'visible': 'true'
        },
    }

    return {
        'page_name': pgettext('lists', 'Топ по Силе'),

        'player': player,

        'header': header,
        'lines': lines,
    }
