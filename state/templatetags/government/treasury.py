from django import template

register = template.Library()
from state.models.treasury import Treasury
from storage.models.storage import Storage


@register.inclusion_tag('state/gov/treasury.html')
def treasury(state):

    treasury = None

    if Treasury.objects.filter(state=state).exists():
        # находим казну государства
        treasury = Treasury.objects.get(state=state)

    return {
        # казна
        'treasury': treasury,
        # класс склада
        'storage_cl': Storage,
    }
