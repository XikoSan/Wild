from django import template
from django.apps import apps
register = template.Library()
from bill.models.bill import Bill
from player.views.get_subclasses import get_subclasses

from regime.regime import Regime
from regime.temporary import Temporary
from regime.presidential import Presidential

@register.inclusion_tag('state/gov/new_bill.html')
def new_bill(player, parliament):

    state_type_cl = None
    # получаем текущий режим из свойств госа
    for regime_cl in Regime.__subclasses__():
        if parliament.state.type == regime_cl.__name__:
            state_type_cl = regime_cl
            break

    bills_classes = get_subclasses(Bill)

    for bill_class in bills_classes:
        if bill_class.__name__ in state_type_cl.forbidden_bills:
            bills_classes.remove(bill_class)

    translate_dict = {}

    for bill_cl in bills_classes:
        if bill_cl.__name__ in state_type_cl.forbidden_bills:
            continue

        translate_dict[bill_cl.__name__] = bill_cl._meta.verbose_name_raw

    return {
        'player': player,
        'parliament': parliament,
        'bills_classes': bills_classes,
        'translate_dict': translate_dict,
    }
