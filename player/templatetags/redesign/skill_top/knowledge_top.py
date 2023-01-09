from django import template
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _
from player.logs.cash_log import CashLog
from player.views.lists.get_thing_page import get_thing_page
from player.player import Player

register = template.Library()

# класс игрока, с местом в рейтинге
class PlayerWithTop(Player):
    pk = 0
    top = 0

    class Meta:
        abstract = True


@register.inclusion_tag('player/redesign/lists/uni_list_templatetag.html')
def knowledge_top(request, player):
    page = request.GET.get('page')
    logs = Player.objects.only('pk', 'image', 'nickname', 'power').all().order_by('-knowledge')[:10]

    players = []
    index = 1

    for line in logs:

        char = PlayerWithTop(
            nickname = line.nickname,
        )
        char.top = index

        char.pk = line.pk
        char.image = line.image
        char.knowledge = line.knowledge

        players.append(char)
        index += 1

    lines = get_thing_page(players, page, 10)

    header = {

        'top': {
            'text': _('Место'),
            'select_text': _('Место'),
            'visible': 'true'
        },

        'image': {
            'text': '',
            'select_text': _('Аватар'),
            'visible': 'true'
        },

        'nickname': {
            'text': _('Никнейм'),
            'select_text': _('Никнейм'),
            'visible': 'true'
        },

        'knowledge': {
            'text': _('Инт'),
            'select_text': _('Инт'),
            'visible': 'true'
        },
    }

    return {
        'page_name': pgettext('skill_top', 'Топ по Интеллекту'),

        'player': player,

        'header': header,
        'lines': lines,
    }
