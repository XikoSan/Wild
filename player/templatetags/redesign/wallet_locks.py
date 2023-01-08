from django import template
from django.utils.translation import pgettext

from player.views.lists.get_thing_page import get_thing_page
from storage.models.cash_lock import CashLock

register = template.Library()


@register.inclusion_tag('player/redesign/lists/uni_list_templatetag.html')
def wallet_locks(request, player):
    page = request.GET.get('page')
    locks = CashLock.objects.filter(lock_player=player, deleted=False)
    lines = get_thing_page(locks, page, 50)

    header = {

        'lock_offer': {
            'get_good_display':
                {
                    'text': pgettext('wallet', 'Товар'),
                    'select_text': pgettext('wallet', 'Товар'),
                    'visible': 'true'
                },
            'count': {
                'text': pgettext('wallet', 'Количество'),
                'select_text': pgettext('wallet', 'Количество'),
                'visible': 'true'
            },
        },

        'lock_cash': {
            'text': pgettext('wallet', 'Блокировано'),
            'select_text': pgettext('wallet', 'Блокировано'),
            'visible': 'true'
        },
    }

    return {
        'page_name': pgettext('wallet', 'Блокировки'),
        'player': player,

        'header': header,
        'lines': lines,
    }
