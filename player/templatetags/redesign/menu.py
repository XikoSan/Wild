from django import template
import redis
from chat.models.messages.chat_members import ChatMembers

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

    return {
        'has_unread': has_unread,
    }
