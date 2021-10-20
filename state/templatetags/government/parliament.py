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
def parliament(state):

    parliament = parliament_voting = \
        next_voting_date = deputates = None

    # если в этом регионе есть государство
    if state:
        # если у государства есть парламент
        if Parliament.objects.filter(state=state).exists():
            parliament = Parliament.objects.get(state=state)
            # если в парламенте идут выборы
            if ParliamentVoting.objects.filter(running=True, parliament=parliament).exists():
                parliament_voting = ParliamentVoting.objects.get(running=True, parliament=parliament)
            else:
                if ParliamentVoting.objects.filter(running=False, parliament=parliament, task__isnull=False).exists():
                    next_voting_date = \
                        ParliamentVoting.objects.get(running=False, parliament=parliament,
                                                     task__isnull=False).voting_start + timedelta(days=7)
                else:
                    next_voting_date = state.foundation_date + timedelta(days=7)
            # если есть парламентские партии
            if ParliamentParty.objects.filter(parliament=parliament).exists():
                # для каждой парламентской партии
                for parl_party in ParliamentParty.objects.filter(parliament=parliament):
                    # получаем экземпляр партии из объекта парламентской партии
                    adding_party = Party.objects.get(pk=parl_party.party.pk)
                    # для каждого игрока этой партии с мандатом
                    for deputate in DeputyMandate.objects.filter(parliament=parliament, party=adding_party):
                        # получаем экземпляр депутата
                        dep_player = Player.objects.filter(pk=deputate.player.pk)
                        # если лист партий из парламента не пустой
                        if deputates:
                            # добавляем партию к списку
                            deputates = list(chain(deputates, dep_player))
                        else:
                            deputates = dep_player

    return {
        # парламент
        'parliament': parliament,

        # партии из парламента
        'parties': ParliamentParty.objects.filter(parliament=parliament),
        # депутаты парламента
        'deputates': deputates,

        # выборы
        'parliament_voting': parliament_voting,
        #  ближайшие выборы
        'next_voting_date': next_voting_date,
    }
