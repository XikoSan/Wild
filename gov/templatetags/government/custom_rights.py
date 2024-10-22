from itertools import chain

from django import template

register = template.Library()
from bill.models.bill import Bill
from player.views.get_subclasses import get_subclasses
from gov.models.minister import Minister
from gov.models.president import President
from gov.models.custom_rights.custom_right import CustomRight


@register.inclusion_tag('state/gov/custom_rights.html')
def custom_rights(player, state):

    rights = []
    translate_dict = {}

    if Minister.objects.filter(player=player, state=state).exists():

        minister = Minister.objects.get(player=player, state=state)

        custom_rights = CustomRight.__subclasses__()

        for right in minister.rights.all():

            for c_right in custom_rights:

                if right.right == c_right.__name__:
                    rights.append(c_right)
                    translate_dict[c_right.__name__] = c_right._meta.verbose_name

    return {
        'player': player,
        'state': state,
        'custom_rights': rights,
        'translate_dict': translate_dict,
    }
