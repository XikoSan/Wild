from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.translation import pgettext

from bill.models.bill import Bill
from player.decorators.player import check_player
from player.player import Player
from player.views.get_subclasses import get_subclasses
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from wild_politics.settings import JResponse


# новый законопроект
@login_required(login_url='/')
@check_player
@transaction.atomic
def new_bill(request):
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

                    bills_count = 0

                    for bill_cl in bills_classes:
                        bills_dict[bill_cl.__name__] = bill_cl

                        bills_count += bill_cl.objects.filter(initiator=player, running=True).count()

                    if bills_count >= 3:
                        data = {
                            'response': pgettext('new_bill', 'Нельзя предложить более трех законов одновременно'),
                            'header': pgettext('new_bill', 'Новый законопроект'),
                            'grey_btn': pgettext('core', 'Закрыть'),
                        }
                        return JResponse(data)

                    bill_type = request.POST.get('bill_type')

                    if bill_type in bills_dict.keys():

                        bill_cl = bills_dict[bill_type]

                        return JResponse(bill_cl.new_bill(request, player, parliament))

                    else:
                        data = {
                            'response': pgettext('new_bill', 'Нет такого вида законопроекта'),
                            'header': pgettext('new_bill', 'Новый законопроект'),
                            'grey_btn': pgettext('core', 'Закрыть'),
                        }
                        return JResponse(data)
                else:
                    data = {
                        'response': 'Вы - не депутат этого парламента',
                        'header': pgettext('new_bill', 'Новый законопроект'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JResponse(data)
            else:
                data = {
                    'response': pgettext('new_bill', 'В этом государстве нет парламента'),
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)
        else:
            data = {
                'response': pgettext('new_bill', 'В этом регионе нет государства'),
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)
    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('new_bill', 'Новый законопроект'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
