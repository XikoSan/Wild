from django import template
from django.utils import timezone
register = template.Library()
from player.logs.skill_training import SkillTraining
import copy

@register.inclusion_tag('player/overview_skills.html')
def skills(player):
    train = None
    has_slot = True

    power_count = knowledge_count = endurance_count = skills_count = 0

    if SkillTraining.objects.filter(player=player).exists():
        # сколько навыков Силы изучается
        power_count = SkillTraining.objects.filter(player=player, skill='power').count()
        # сколько навыков Интеллекта изучается
        knowledge_count = SkillTraining.objects.filter(player=player, skill='knowledge').count()
        # сколько навыков Вынки изучается
        endurance_count = SkillTraining.objects.filter(player=player, skill='endurance').count()

        skills_count = SkillTraining.objects.filter(player=player).count() - 1

        if skills_count >= 5:
            has_slot = False

        train = SkillTraining.objects.filter(player=player).order_by('end_dtime').first()

    premium = False

    if player.premium > timezone.now():
        premium = True

    queue = copy.deepcopy(SkillTraining.objects.filter(player=player).order_by('end_dtime')[1:])

    last_skill = None
    # при попытке взять .last() ругается, херня какая-то
    for q in queue:
        last_skill = q

    return {
        # игрок
        'player': player,
        # признак према
        'premium': premium,
        # изучаемый навык
        'train': train,

        # сколько навыков Силы изучается
        'power_count': power_count,
        # сколько навыков Интеллекта изучается
        'knowledge_count': knowledge_count,
        # сколько навыков Вынки изучается
        'endurance_count': endurance_count,

        # есть место для добавления навыка в очередь
        'has_slot': has_slot,
        # количество навыков в очереди
        'skills_count': skills_count,
        # очередь изучения
        'queue': queue,
        # последний навык в очереди изучения
        'last_skill': last_skill,
    }
