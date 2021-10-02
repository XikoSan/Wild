from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from itertools import chain

from player.player import Player
from region.region import Region

from player.decorators.player import check_player
from party.party import Party
from state.models.parliament.parliament import Parliament
from state.models.parliament.parliament_voting import ParliamentVoting
from state.models.parliament.parliament_party import ParliamentParty
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.treasury import Treasury
from state.views.get_subclasses import get_subclasses


# страница правительства государства
@login_required(login_url='/')
@check_player
def government(request):
    # получаем персонажа
    player = Player.objects.get(account=request.user)
    # признак того, что он депутат - может голосовать, предлагать законы
    is_deputy = None
    with_bill = None
    state = None
    treasury = None
    parliament = None
    parliament_voting = None
    next_voting_date = None
    capital = None
    state_regions = None
    bills_list = None
    bill_timings = {}
    bill_voted = {}
    # листы регион - состояние сколько можно разведать
    gold_status = {}
    oil_status = {}
    ore_status = {}
    gold_first = None
    # листы регион - состояние зданий
    med_status = {}
    dpt_status = {}
    med_first = None
    # первый регион в списке разведки ресурсов
    pk_first = None
    first_filled = None
    # общий список депутатов
    deputates = None
    # если в этом регионе есть государство
    if player.region.state:
        state = player.region.state
        # находим столицу
        capital = Region.objects.get(capital=state)
        # находим казну государства
        treasury = Treasury.objects.get(state=state)
        # если у государства есть парламент
        if Parliament.objects.filter(state=state).exists():
            parliament = Parliament.objects.get(state=state)
            # если в парламенте идут выборы
            if ParliamentVoting.objects.filter(running=True, parliament=parliament).exists():
                parliament_voting = ParliamentVoting.objects.get(running=True, parliament=parliament)
            else:
                if ParliamentVoting.objects.filter(running=False, parliament=parliament).exists():
                    next_voting_date = \
                        ParliamentVoting.objects.filter(running=False, parliament=parliament).order_by('-voting_end')[
                            0].voting_end + timedelta(days=7)
            # # если есть парламентские партии
            # if ParliamentParty.objects.filter(parliament=parliament).exists():
            #     # для каждой парламентской партии
            #     for parl_party in ParliamentParty.objects.filter(parliament=parliament):
            #         # получаем экземпляр партии из объекта парламентской партии
            #         adding_party = Party.objects.get(pk=parl_party.party.pk)
            #         # для каждого игрока этой партии с мандатом
            #         for deputate in DeputyMandate.objects.filter(parliament=parliament, party=adding_party):
            #             # получаем экземпляр депутата
            #             dep_player = Player.objects.filter(pk=deputate.player.pk)
            #             # если лист партий из парламента не пустой
            #             if deputates:
            #                 # добавляем партию к списку
            #                 deputates = list(chain(deputates, dep_player))
            #             else:
            #                 deputates = dep_player
            #     # Если сам игрок - депутат в этом парламенте:
            #     if DeputyMandate.objects.filter(player=player, parliament=parliament).exists():
            #         is_deputy = True
            #         # ставил ли он законы в парламенте
            #         # ищем законы этого парламента
            #         bills_types = get_subclasses(Bill)
            #         # для каждого типа законопроектов:
            #         for type in bills_types:
            #             # если есть активные законы от этого человека в этом парламенте
            #             if type.objects.filter(initiator=player,
            #                                    parliament=Parliament.objects.get(state=player.region.state),
            #                                    running=True).exists():
            #                 with_bill = True
            #             # если нет, то имеет смысл провести подсчеты для законопроектов
            #             else:
            #                 # сколько можно разведать в регионах государства
            #                 state_regions = Region.objects.filter(state=state).order_by('-capital', 'id')
            #                 for s_region in state_regions:
            #                     if first_filled == None:
            #                         med_first = s_region.med_lvl
            #                         first_filled = True
            #                     # построено зданий в регионах государства
            #                     med_status[s_region] = s_region.med_lvl
            #                     dpt_status[s_region] = s_region.dpt_lvl
            #
            # # ищем законы этого парламента
            # bills_types = get_subclasses(Bill)
            # # для каждого типа законопроектов:
            # for type in bills_types:
            #     # если есть активные законы в этом парламенте
            #     if type.objects.filter(parliament=parliament, running=True).exists():
            #         # если лист партий из парламента не пустой
            #         if bills_list:
            #             # добавляем в список на вывод
            #             bills_list = list(chain(bills_list, type.objects.filter(parliament=parliament, running=True)))
            #         else:
            #             bills_list = type.objects.filter(parliament=parliament, running=True)
            # # если список активных законопроектов не пуст
            # if bills_list:
            #     for bill in bills_list:
            #         # осталось времени в секундах до конца голосования
            #         bill_timings[bill] = BillCDinSeconds(bill)
            #         # узнаем, голосовал ли игрок за этот ЗП
            #         votes_pro = bill.votes_pro.all()
            #         votes_con = bill.votes_con.all()
            #         if player in votes_pro:
            #             # если голосовал
            #             bill_voted[bill] = 'pro'
            #         elif player in votes_con:
            #             # если голосовал против
            #             bill_voted[bill] = 'con'
            #         else:
            #             # если НЕ голосовал
            #             bill_voted[bill] = 'none'

    # отправляем в форму
    return render(request, 'gamecore/main_menu/Government/Government.html', {
        # самого игрока
        'player': player,
        # государство, в котором сейчас находится игрок
        'state': state,
        # столица государства
        'capital': capital,
        # дата ближайших выборов
        'next_voting_date': next_voting_date,

        # # признак того, что он депутат
        # 'is_deputy': is_deputy,
        # # признак того, что он ставил законы в парламенте
        # 'with_bill': with_bill,
        # # регионы государства
        # 'state_regions': state_regions,
        # # казна этого государства
        # 'treasury': treasury,

    })
