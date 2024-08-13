from django import template
from django.utils import timezone

register = template.Library()
from player.logs.skill_training import SkillTraining
import copy
from django.apps import apps


@register.inclusion_tag('player/redesign/player_help.html')
def player_help(player):
    return {
        # игрок
        'player': player,
    }
