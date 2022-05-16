from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from bill.models.bill import Bill
from gov.models.minister import Minister
from player.decorators.player import check_player
from player.player import Player
from player.views.get_subclasses import get_subclasses
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament_party import ParliamentParty
import copy

# управление министрами
@login_required(login_url='/')
@check_player
def ministers_manage(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    deputates = None
    parl_parties = []
    bills_dict = {}
    points = 0

    if DeputyMandate.objects.filter(player=player, is_president=True).exists():
        # мандат президента
        pres_mandate = DeputyMandate.objects.get(player=player, is_president=True)

        ministers_list = []

        # министры
        ministers = Minister.objects.filter(state=pres_mandate.parliament.state)

        for minister in ministers:
            ministers_list.append(minister.player)

        # если есть парламентские партии
        if ParliamentParty.objects.filter(parliament=pres_mandate.parliament).exists():
            # для каждой парламентской партии
            for parl_party in ParliamentParty.objects.filter(parliament=pres_mandate.parliament):
                # получаем экземпляр партии из объекта парламентской партии
                parl_parties.append(parl_party.party)

            # депутаты этой партии
            deputates = DeputyMandate.objects.filter(parliament=pres_mandate.parliament,
                                                     party__in=parl_parties,
                                                     is_president=False,
                                                     player__isnull=False,
                                                     ).exclude(
                                                     player__in=ministers_list
                                                    ).order_by('player')

        # число использованных очков
        points = ministers.count() * 3

        for minister in ministers:
            points += minister.rights.count()
        # сколько очков осталось
        points = 10 - points

        # законопроекты, на которые они имеют право
        bills_classes = get_subclasses(Bill)

        bills_classes_tmp = copy.copy(bills_classes)

        for cl in bills_classes:
            # менять форму правления быстро нельзя
            if cl.__name__ in ['ChangeForm']:
                bills_classes_tmp.remove(cl)

        bills_classes = copy.copy(bills_classes_tmp)

        for bill_cl in bills_classes:
            bills_dict[bill_cl.__name__] = bill_cl._meta.verbose_name_raw

        # отправляем в форму
        return render(request, 'gov/ministers_manage.html',
                      {'player': player,

                       'deputates': deputates,
                       'ministers': ministers,
                       'points': points,

                       'bills_classes': bills_classes,
                       'bills_dict': bills_dict,

                       'page_name': 'Министры',
                       })
    else:
        return redirect('government')
