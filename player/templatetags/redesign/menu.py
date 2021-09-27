from django import template

# from gamecore.all_views.header.until_recharge import UntilRecharge
register = template.Library()


@register.inclusion_tag('player/redesign/menu.html')
def menu():
    return {
        # 'player': player,
        # 'countdown': UntilRecharge(player)
    }
