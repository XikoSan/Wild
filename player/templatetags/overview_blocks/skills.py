from django import template
from django.utils import timezone
register = template.Library()
from player.logs.skill_training import SkillTraining


@register.inclusion_tag('player/overview_skills.html')
def skills(player):
    train = None
    if SkillTraining.objects.filter(player=player).exists():
        train = SkillTraining.objects.filter(player=player).order_by('end_dtime').first()

    premium = False

    if player.premium > timezone.now():
        premium = True

    return {
        # игрок
        'player': player,
        # признак према
        'premium': premium,
        # изучаемый навык
        'train': train,
    }
