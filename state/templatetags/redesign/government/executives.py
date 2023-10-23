from django import template

register = template.Library()
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament_party import ParliamentParty
from gov.models.minister import Minister
import random


@register.inclusion_tag('state/redesign/gov/executives.html')
def executives(player, parliament):
    deputates = None
    pres_mandate = ministers = None

    # если у государства есть парламент
    if parliament:
        # если есть президентский мандат
        if DeputyMandate.objects.filter(parliament=parliament, is_president=True).exists():
            # мандат президента
            pres_mandate = DeputyMandate.objects.get(parliament=parliament, is_president=True)
            # министры
            ministers = Minister.objects.filter(state=parliament.state)

    return {
        'player': player,

        # мандат президента
        'pres_mandate': pres_mandate,
        # министры
        'ministers': ministers,
    }
