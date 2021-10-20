from datetime import timedelta
from itertools import chain

from django import template

register = template.Library()
from party.party import Party
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.parliament.parliament_party import ParliamentParty
from state.models.parliament.parliament_voting import ParliamentVoting
from player.player import Player


@register.inclusion_tag('state/gov/parliament.html')
def parliament(parliament):

    deputates = None

    # если у государства есть парламент
    if parliament:
        # если есть парламентские партии
        if ParliamentParty.objects.filter(parliament=parliament).exists():
            # для каждой парламентской партии
            for parl_party in ParliamentParty.objects.filter(parliament=parliament):
                # получаем экземпляр партии из объекта парламентской партии
                adding_party = Party.objects.get(pk=parl_party.party.pk)

                # депутаты этой партии
                party_deputates = DeputyMandate.objects.filter(parliament=parliament, party=adding_party).order_by('player')

                # если лист игроков из парламента не пустой
                if deputates:
                    # добавляем партию к списку
                    deputates = list(chain(deputates, party_deputates))
                else:
                    deputates = party_deputates

    return {
        # парламент
        'parliament': parliament,

        # партии из парламента
        'parties': ParliamentParty.objects.filter(parliament=parliament),
        # депутаты парламента
        'deputates': deputates,
    }
