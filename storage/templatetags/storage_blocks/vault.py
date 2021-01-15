from django import template

register = template.Library()


@register.inclusion_tag('storage/storage_blocks/vault.html')
def vault(player):

    return {
        'player': player,
    }
