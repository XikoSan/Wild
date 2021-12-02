from django import template

register = template.Library()
from state.models.bills.bill import Bill
from player.views.get_subclasses import get_subclasses


@register.inclusion_tag('state/gov/new_bill.html')
def new_bill(player, parliament):
    bills_classes = get_subclasses(Bill)

    translate_dict = {}

    for bill_cl in bills_classes:
        translate_dict[bill_cl.__name__] = bill_cl._meta.verbose_name_raw

    return {
        'player': player,
        'parliament': parliament,
        'bills_classes': bills_classes,
        'translate_dict': translate_dict,
    }
