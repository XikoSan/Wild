import redis
from django import template
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _
from player.logs.cash_log import CashLog
from player.player import Player
from player.views.lists.get_thing_page import get_thing_page
from party.party import Party
import datetime
register = template.Library()


def create_temporary_player_class():
    # класс партии, в котором её место в топе - это поле
    class PartyWithProduced(Party):
        pk = 0
        mined = 0
        reward = 0

        class Meta:
            proxy = True

    return PartyWithProduced


@register.inclusion_tag('player/redesign/lists/uni_list_templatetag.html')
def factory_top(request, player):
    page = request.GET.get('page')

    all_produced = 0
    date_string = "2023-11-20"
    date = datetime.date.fromisoformat(date_string)

    r = redis.StrictRedis(host='redis', port=6379, db=0)

    parties = Party.objects.only('pk', 'image', 'title').filter(deleted=False)

    if datetime.datetime.now().date() < date:
        for party in parties:
            # берем сколько она добыла за неделю
            if r.exists("party_factory_" + str(party.pk)):
                all_produced += int(float(r.get("party_factory_" + str(party.pk))))
    else:
        if r.exists("all_factory"):
            all_produced = int(float(r.get("all_factory")))

    mining_dict = {}

    for party in parties:
        if r.exists("party_factory_" + str(party.pk)):
            mining_dict[party] = int(float(r.get("party_factory_" + str(party.pk))))

    sorted_items = sorted(mining_dict.items(), key=lambda x: x[1], reverse=True)[:10]

    result_list = [(key, value) for key, value in sorted_items]

    parties_with_size = []

    for party_tuple in result_list:
        PartyWithProduced = create_temporary_player_class()

        size_party = PartyWithProduced(
            title = party_tuple[0].title,
            image = party_tuple[0].image,
        )
        size_party.pk = party_tuple[0].pk,

        size_party.mined = party_tuple[1]
        if all_produced > 0:
            size_party.reward = int(10000 * (party_tuple[1] / all_produced))

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
            'text': pgettext('lists', 'Произведено'),
            'select_text': pgettext('lists', 'Произведено'),
            'visible': 'true'
        },

        'reward': {
            'text': '',
            'select_text': pgettext('lists', 'Награда'),
            'visible': 'true'
        },
    }

    return {
        'page_name': pgettext('skill_top', 'Топ производства'),

        'player': player,

        'header': header,
        'lines': lines,
    }
