from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from player.player import Player
from player.views.get_subclasses import get_subclasses
from bill.models.bill import Bill
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.tasks import run_bill
from wild_politics.settings import JResponse


# новый законопроект
@login_required(login_url='/')
@check_player
@transaction.atomic
def vote_bill(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        # если в этом регионе есть государство
        if player.region.state:
            # если у государства есть парламент
            if Parliament.objects.filter(state=player.region.state).exists():
                parliament = Parliament.objects.get(state=player.region.state)
                # проверяем, депутат ли этого парла игрок или нет
                if DeputyMandate.objects.filter(player=player, parliament=parliament).exists():

                    bills_classes = get_subclasses(Bill)

                    bills_dict = {}

                    for bill_cl in bills_classes:
                        bills_dict[bill_cl.__name__] = bill_cl

                    bill_type = request.POST.get('bill_type')

                    if bill_type in bills_dict.keys():

                        if bills_dict[bill_type].objects.filter(running=True, pk=int(request.POST.get('pk'))).exists():

                            bill = bills_dict[bill_type].objects.select_for_update().get(pk=int(request.POST.get('pk')))

                            votes_pro = bill.votes_pro.all()
                            votes_con = bill.votes_con.all()

                            # если игрок еще не голосовал
                            if not player in votes_pro \
                                    and not player in votes_con:

                                if request.POST.get('mode') == 'pro':
                                    bill.votes_pro.add(player)

                                elif request.POST.get('mode') == 'con':
                                    bill.votes_con.add(player)

                                else:
                                    data = {
                                        'response': 'Надо проголосовать!',
                                        'header': 'Голосование',
                                        'grey_btn': 'Закрыть',
                                    }
                                    return JResponse(data)

                                # если досрочное принятие разрешено
                                if bill.accept_ahead:
                                    # если после голосования голосов стало больше, чем процент досрочного принятия
                                    #           то принимаем законопроект
                                    if bill.votes_pro.count() * 100 / DeputyMandate.objects.filter(player__isnull=False, parliament=parliament).count() >= bill.ahead_percent \
                                            or bill.votes_con.count() * 100 / DeputyMandate.objects.filter(player__isnull=False, parliament=parliament).count() >= bill.ahead_percent:
                                        run_bill.apply_async(у
                                            (bill.__class__.__name__, bill.pk),
                                            retry=False
                                        )

                                data = {
                                    'response': 'ok',
                                }
                                return JResponse(data)

                            else:
                                data = {
                                    'response': 'Вы уже проголосовали',
                                    'header': 'Голосование',
                                    'grey_btn': 'Закрыть',
                                }
                                return JResponse(data)
                        else:
                            data = {
                                'response': 'Нет такого законопроекта',
                                'header': 'Голосование',
                                'grey_btn': 'Закрыть',
                            }
                            return JResponse(data)
                    else:
                        data = {
                            'response': 'Нет такого вида законопроекта',
                            'header': 'Голосование',
                            'grey_btn': 'Закрыть',
                        }
                        return JResponse(data)
                else:
                    data = {
                        'response': 'Вы - не депутат этого парламента',
                        'header': 'Голосование',
                        'grey_btn': 'Закрыть',
                    }
                    return JResponse(data)
            else:
                data = {
                    'response': 'В этом государстве нет парламента',
                    'header': 'Голосование',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)
        else:
            data = {
                'response': 'В этом регионе нет государства',
                'header': 'Голосование',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)
    # если страницу только грузят
    else:
        data = {
            'response': 'Ошибка типа запроса',
            'header': 'Основание государства',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
