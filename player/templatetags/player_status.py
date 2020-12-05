from django import template

# from gamecore.all_views.header.until_recharge import UntilRecharge
register = template.Library()


@register.inclusion_tag('player/player_status.html')
def player_status(player):
    return {
        'player': player,
        # 'countdown': UntilRecharge(player)
    }
