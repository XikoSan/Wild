from itertools import chain

from django import template

register = template.Library()
from state.models.bills.bill import Bill
from player.views.get_subclasses import get_subclasses


@register.inclusion_tag('state/gov/bills.html')
def bills(player, parliament):
    bills_list = []

    bills_classes = get_subclasses(Bill)

    # для каждого типа законопроектов:
    for type in bills_classes:
        # если есть активные законы в этом парламенте
        if type.objects.filter(parliament=parliament, running=True).exists():
            # если лист партий из парламента не пустой
            if bills_list:
                # добавляем в список на вывод
                bills_list = list(chain(bills_list, type.objects.filter(parliament=parliament, running=True)))
            else:
                bills_list = type.objects.filter(parliament=parliament, running=True)

    if bills_list:
        bills_list = sorted(bills_list, key=lambda bill: bill.voting_start)

    return {
        'player': player,
        'bills_list': bills_list,
    }
