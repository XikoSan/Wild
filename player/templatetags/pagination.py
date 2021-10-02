from django import template

# from gamecore.all_views.header.until_recharge import UntilRecharge
register = template.Library()


@register.inclusion_tag('lists/pagination.html')
def pagination(page):
    return {
        'page': page,
    }
