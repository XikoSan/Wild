from itertools import chain

from django import template

register = template.Library()
from state.models.bills.bill import Bill
from player.views.get_subclasses import get_subclasses


@register.inclusion_tag('state/gov/bills_history.html')
def bills_history(player, parliament):
    bills_list = None

    bills_classes = get_subclasses(Bill)

    # для каждого типа законопроектов:
    for type in bills_classes:
        # если есть рассмотренные законы в этом парламенте
        if type.objects.filter(parliament=parliament, running=False).exists():
            # если лист партий из парламента не пустой
            if bills_list:
                # добавляем в список на вывод
                bills_list = list(chain(bills_list, type.objects.filter(parliament=parliament, running=False)))
            else:
                bills_list = type.objects.filter(parliament=parliament, running=False)

    return {
        'player': player,
        'bills_list': bills_list,
    }
