from itertools import chain

from django import template

register = template.Library()
from bill.models.bill import Bill
from player.views.get_subclasses import get_subclasses
from gov.models.minister import Minister
from gov.models.president import President

@register.inclusion_tag('state/redesign/bills.html')
def bills(player, parliament):
    bills_list = []
    minister = president = None

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

    if Minister.objects.filter(state=parliament.state, player=player).exists():
        minister = Minister.objects.get(state=parliament.state, player=player)

    if President.objects.filter(state=parliament.state, leader__isnull=False).exists():
        president = President.objects.get(state=parliament.state).leader

    return {
        'player': player,
        'minister': minister,
        'president': president,
        'bills_list': bills_list,
    }
