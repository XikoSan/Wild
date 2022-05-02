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
import random

@register.inclusion_tag('state/gov/parliament.html')
def parliament(player, parliament):

    deputates = None
    pres_mandate = None

    party_colors = {}

    # если у государства есть парламент
    if parliament:
        # если есть президентский мандат
        if DeputyMandate.objects.filter(parliament=parliament, is_president=True).exists():
            pres_mandate = DeputyMandate.objects.get(parliament=parliament, is_president=True)
        # если есть парламентские партии
        if ParliamentParty.objects.filter(parliament=parliament).exists():
            # для каждой парламентской партии
            for parl_party in ParliamentParty.objects.filter(parliament=parliament):

                party_colors[parl_party] = "%06x" % random.randint(0, 0xFFFFFF)

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
    }
