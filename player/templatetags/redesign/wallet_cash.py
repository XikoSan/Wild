from django import template

from storage.models.storage import Storage
from django.utils.translation import pgettext
from player.views.lists.get_thing_page import get_thing_page

register = template.Library()


@register.inclusion_tag('player/redesign/lists/uni_list_templatetag.html')
def wallet_cash(request, player):
    page = request.GET.get('page')
    storages = Storage.actual.filter(owner=player).only('region', 'cash')
    lines = get_thing_page(storages, page, 50)

    header = {
        'region': {
            'text': pgettext('wallet', 'Регион'),
            'select_text': pgettext('wallet', 'Регион'),
            'visible': 'true'
        },

        'cash': {
            'text': pgettext('wallet', 'Наличные'),
            'select_text': pgettext('wallet', 'Наличные'),
            'visible': 'true'
        },
    }

    return {
        'page_name': pgettext('wallet', 'Наличные'),
        'player': player,

        'header': header,
        'lines': lines,
    }
