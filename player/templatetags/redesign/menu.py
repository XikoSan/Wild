from django import template
import redis
from party.primaries.primaries import Primaries
from party.primaries.primaries_bulletin import PrimBulletin


# from gamecore.all_views.header.until_recharge import UntilRecharge
register = template.Library()


@register.inclusion_tag('player/redesign/menu.html')
def menu(player):

    has_unread = False
    r = redis.StrictRedis(host='redis', port=6379, db=0)
    unread_dict = r.hgetall(f'chats_{player.pk}_unread')

    for dialog in unread_dict.keys():
        if unread_dict[dialog] and int(unread_dict[dialog]) > 0:
            has_unread = True
            break

    active_primaries = False
    voted_primaries = False

    if player.party and Primaries.objects.filter(running=True, party=player.party):
        active_primaries = True

        if PrimBulletin.objects.filter(primaries=Primaries.objects.filter(running=True, party=player.party)[0],
                                                                                                player=player).exists():
            voted_primaries = True


    return {
        'player': player,
        'has_unread': has_unread,

        'active_primaries': active_primaries,
        'voted_primaries': voted_primaries,
    }
