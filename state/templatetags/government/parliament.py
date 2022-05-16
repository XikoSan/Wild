from django import template

register = template.Library()
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament_party import ParliamentParty
from gov.models.minister import Minister
import random


@register.inclusion_tag('state/gov/parliament.html')
def parliament(player, parliament):
    deputates = None
    pres_mandate = ministers = None

    party_colors = {}
    parl_parties = []

    # если у государства есть парламент
    if parliament:
        # если есть президентский мандат
        if DeputyMandate.objects.filter(parliament=parliament, is_president=True).exists():
            # мандат президента
            pres_mandate = DeputyMandate.objects.get(parliament=parliament, is_president=True)
            # министры
            ministers = Minister.objects.filter(state=parliament.state)

        # если есть парламентские партии
        if ParliamentParty.objects.filter(parliament=parliament).exists():
            # для каждой парламентской партии
            for parl_party in ParliamentParty.objects.filter(parliament=parliament):
                party_colors[parl_party] = "%06x" % random.randint(0, 0xFFFFFF)

                # получаем экземпляр партии из объекта парламентской партии
                parl_parties.append(parl_party.party)

            # депутаты этой партии
            deputates = DeputyMandate.objects.filter(parliament=parliament, party__in=parl_parties).order_by('player')

    return {
        'player': player,

        # парламент
        'parliament': parliament,

        # партии из парламента
        'parties': ParliamentParty.objects.filter(parliament=parliament),
        # рандомные цвета парламентских партий
        'party_colors': party_colors,
        # депутаты парламента
        'deputates': deputates,

        # мандат президента
        'pres_mandate': pres_mandate,
        # министры
        'ministers': ministers,
    }
