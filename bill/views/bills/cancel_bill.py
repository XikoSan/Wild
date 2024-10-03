from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from player.decorators.player import check_player
from player.player import Player
from player.views.get_subclasses import get_subclasses
from bill.models.bill import Bill
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from wild_politics.settings import JResponse
from django.utils.translation import pgettext


# отменить законопроект
@login_required(login_url='/')
@check_player
@transaction.atomic
def cancel_bill(request):
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

                            # если игрок - автор законопроекта
                            if player == bill.initiator:

                                bill.bill_cancel()

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
                                    'response': pgettext('cancel_bill', 'Вы не автор законопроекта'),
                                    'header': pgettext('cancel_bill', 'Отмена законопроекта'),
                                    'grey_btn': pgettext('core', 'Закрыть'),
                                }
                                return JResponse(data)
                        else:
                            data = {
                                'response': pgettext('cancel_bill', 'Нет такого законопроекта'),
                                'header': pgettext('cancel_bill', 'Отмена законопроекта'),
                                'grey_btn': pgettext('core', 'Закрыть'),
                            }
                            return JResponse(data)
                    else:
                        data = {
                            'response': pgettext('cancel_bill', 'Нет такого вида законопроекта'),
                            'header': pgettext('cancel_bill', 'Отмена законопроекта'),
                            'grey_btn': pgettext('core', 'Закрыть'),
                        }
                        return JResponse(data)
                else:
                    data = {
                        'response': pgettext('cancel_bill', 'Вы - не депутат этого парламента'),
                        'header': pgettext('cancel_bill', 'Отмена законопроекта'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JResponse(data)
            else:
                data = {
                    'response': pgettext('cancel_bill', 'В этом государстве нет парламента'),
                    'header': pgettext('cancel_bill', 'Отмена законопроекта'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)
        else:
            data = {
                'response': pgettext('cancel_bill', 'В этом регионе нет государства'),
                'header': pgettext('cancel_bill', 'Отмена законопроекта'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)
    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('cancel_bill', 'Отмена законопроекта'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
