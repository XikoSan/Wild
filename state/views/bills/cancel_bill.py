from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from player.decorators.player import check_player
from player.player import Player
from player.views.get_subclasses import get_subclasses
from state.models.bills.bill import Bill
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from wild_politics.settings import JResponse


# отменить законопроект
@login_required(login_url='/')
@check_player
@transaction.atomic
def cancel_bill(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.get(account=request.user)

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

                            # если игрок - автор законопроекта
                            if player == bill.initiator:

                                task = bill.task
                                bill.task = None
                                bill.save()

                                task.delete()

                                bill.type = 'cn'
                                bill.running = False
                                bill.voting_end = timezone.now()
                                bill.save()

                                data = {
                                    'response': 'ok',
                                }
                                return JResponse(data)

                            else:
                                data = {
                                    'response': 'Вы не автор законопроекта',
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
