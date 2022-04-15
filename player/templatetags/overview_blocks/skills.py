from django import template

register = template.Library()
from player.logs.skill_training import SkillTraining


@register.inclusion_tag('player/overview_skills.html')
def skills(player):
    train = None
    if SkillTraining.objects.filter(player=player).exists():
        train = SkillTraining.objects.filter(player=player).order_by('end_dtime').first()

    return {
        # игрок
        'player': player,
        # изучаемый навык
        'train': train,
    }
