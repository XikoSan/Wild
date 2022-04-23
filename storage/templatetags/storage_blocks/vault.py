from django import template

register = template.Library()
from django.utils import timezone

@register.inclusion_tag('storage/storage_blocks/vault.html')
def vault(player):

    premium = False
    if player.premium > timezone.now():
        premium = True

    return {
        'player': player,
        'premium': premium,
    }
