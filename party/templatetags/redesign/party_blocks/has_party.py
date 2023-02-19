from django import template

register = template.Library()
from party.party import Party
from player.player import Player
from party.primaries.primaries_leader import PrimariesLeader
from party.primaries.primaries import Primaries
from party.logs.party_apply import PartyApply
from party.position import PartyPosition
from datetime import datetime
from wild_politics.settings import TIME_ZONE
import pytz
import redis

@register.inclusion_tag('party/redesign/party_blocks/has_party.html')
def has_party(player):
    # идущие праймериз
    prims = None
    # лидер предыдущих праймериз
    last_prim_lead = None
    if PrimariesLeader.objects.filter(party=player.party).exists():
        last_prim_lead = PrimariesLeader.objects.get(party=player.party)
    # отправляем в форму
    if Primaries.objects.filter(party=Party.objects.get(pk=player.party.pk), running=True).exists():
        prims = Primaries.objects.get(party=player.party, running=True)

    online_dict = {}
    r = redis.StrictRedis(host='redis', port=6379, db=0)

    for char in Player.objects.filter(party=player.party):
        timestamp = None
        timestamp = r.hget('online', str(char.pk))
        if timestamp:
            online_dict[char.pk] = datetime.fromtimestamp(int(timestamp)).replace(tzinfo=pytz.timezone(TIME_ZONE)).astimezone(
                tz=pytz.timezone(player.time_zone)).strftime("%d.%m.%Y %H:%M:%S")
        else:
            online_dict[char.pk] = None

    return {
        # игрок
        'player': player,

        'members_count': Player.objects.filter(party=player.party).count(),
        'requests_count': PartyApply.objects.filter(party=player.party, status='op').count(),
        'players_list': Player.objects.filter(party=player.party),
        'roles_list': PartyPosition.objects.filter(party=player.party),
        'primaries': prims,
        'prev_lead': last_prim_lead,
        'online_dict': online_dict
    }
