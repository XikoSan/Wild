from django import template

from skill.models.scouting import Scouting

register = template.Library()


@register.filter(name='scouting')
def scouting(dmg, char):
    if Scouting.objects.filter(player=char, level__gt=0).exists():
        scouting_obj = Scouting.objects.get(player=char)
        return scouting_obj.apply({'sum': dmg, 'not_floor': True})

    else:
        return dmg
