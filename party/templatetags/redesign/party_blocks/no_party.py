from django import template

from party.party import Party
from party.logs.party_apply import PartyApply
from player.player import Player

register = template.Library()


@register.inclusion_tag('party/redesign/party_blocks/no_party.html')
def no_party(player):
    partys = reversed(Party.objects.all())
    party_sizes = {}
    for party in partys:
        party_sizes[party] = Player.objects.filter(party=party).count()

    reg_partys = reversed(Party.objects.filter(region=player.region, deleted=False))
    reg_party_sizes = {}
    for reg_party in reg_partys:
        reg_party_sizes[reg_party] = Player.objects.filter(party=reg_party).count()

    pt_partys = Party.objects.filter(type='pt')
    requests = {}
    for req_party in pt_partys:
        if PartyApply.objects.filter(player=player, party=req_party, status='op').exists():
            requests[req_party] = True
        else:
            requests[req_party] = False

    return {
        # игрок
        'player': player,
        # запросы игрока в партии
        'requests': requests,

        # количество партий в регионе
        'regional_count': Party.objects.filter(region=player.region, deleted=False).count(),
        # региональные партии
        'regional_parties': reversed(Party.objects.filter(region=player.region, deleted=False)),
        # их размеры
        'rg_sizes': reg_party_sizes,

        # партий в игре всего
        'party_count': Party.objects.filter(deleted=False).count(),
        # все партии
        'all_parties': reversed(Party.objects.filter(deleted=False)),
        # их размеры
        'sizes': party_sizes
    }
