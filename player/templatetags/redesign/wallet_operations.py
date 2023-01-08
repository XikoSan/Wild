from django import template
from django.utils.translation import pgettext
from player.logs.cash_log import CashLog
from player.views.lists.get_thing_page import get_thing_page

register = template.Library()


@register.inclusion_tag('player/redesign/lists/uni_list_templatetag.html')
def wallet_operations(request, player):
    page = request.GET.get('page')
    logs = CashLog.objects.filter(player=player).order_by('-dtime')
    lines = get_thing_page(logs, page, 50)

    header = {

        'dtime': {
            'text': pgettext('wallet', 'Время'),
            'select_text': pgettext('wallet', 'Время'),
            'visible': 'true'
        },

        'cash': {
            'text': pgettext('wallet', 'Изменение'),
            'select_text': pgettext('wallet', 'Изменение'),
            'visible': 'true'
        },

        'get_activity_txt_display': {
            'text': pgettext('wallet', 'Описание'),
            'select_text': pgettext('wallet', 'Описание'),
            'visible': 'true'
        },
    }

    return {
        'page_name': pgettext('wallet', 'Операции'),
        'player': player,

        'header': header,
        'lines': lines,
    }
