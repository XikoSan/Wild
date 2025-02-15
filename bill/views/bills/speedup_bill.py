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
from gov.models.minister import Minister
from gov.models.president import President
from django.utils.translation import pgettext

# новый законопроект
@login_required(login_url='/')
@check_player
@transaction.atomic
def speedup_bill(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        # если в этом регионе есть государство
        if player.region.state:
            # если у государства есть парламент
            if Parliament.objects.filter(state=player.region.state).exists():
                parliament = Parliament.objects.get(state=player.region.state)
                # проверяем, депутат ли этого парла игрок или нет
                if not DeputyMandate.objects.filter(player=player, parliament=parliament).exists():
                    data = {
                        'response': pgettext('speedup_bill', 'Вы - не депутат этого парламента'),
                        'header': pgettext('speedup_bill', 'Досрочное принятие'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JResponse(data)

                minister = None
                if not Minister.objects.filter(state=parliament.state, player=player).exists():
                    data = {
                        'response': pgettext('speedup_bill', 'Вы - не министр этого государства'),
                        'header': pgettext('speedup_bill', 'Досрочное принятие'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JResponse(data)
                    
                minister = Minister.objects.get(state=parliament.state, player=player)

                bills_classes = get_subclasses(Bill)

                bills_dict = {}

                for bill_cl in bills_classes:
                    bills_dict[bill_cl.__name__] = bill_cl

                bill_type = request.POST.get('bill_type')

                if bill_type in bills_dict.keys():
                    has_right = False
                    for right in minister.rights.all():
                        if bill_type == right.right:
                            has_right = True
                            break

                    if not has_right:
                        data = {
                            'response': pgettext('speedup_bill', 'Нет права досрочно принимать этот законопроект'),
                            'header': pgettext('speedup_bill', 'Досрочное принятие'),
                            'grey_btn': pgettext('core', 'Закрыть'),
                        }
                        return JResponse(data)

                    if bills_dict[bill_type].objects.filter(running=True, pk=int(request.POST.get('pk'))).exists():

                        bill = bills_dict[bill_type].objects.select_for_update().get(pk=int(request.POST.get('pk')))

                        if President.objects.filter(state=parliament.state, leader__isnull=False).exists():
                            president = President.objects.get(state=parliament.state).leader

                        else:
                            data = {
                                'response': pgettext('speedup_bill', 'В вашем государстве нет лидера'),
                                'header': pgettext('speedup_bill', 'Досрочное принятие'),
                                'grey_btn': pgettext('core', 'Закрыть'),
                            }
                            return JResponse(data)

                        votes_pro = bill.votes_pro.all()
                        votes_con = bill.votes_con.all()

                        if player in votes_con:
                            data = {
                                'response': 'Вы проголосовали против, досрочное принятие невозможно',
                                'header': pgettext('speedup_bill', 'Досрочное принятие'),
                                'grey_btn': pgettext('core', 'Закрыть'),
                            }
                            return JResponse(data)

                        if not president in votes_pro:
                            data = {
                                'response': pgettext('speedup_bill', 'Лидер государства ещё не подписал этот законопроект'),
                                'header': pgettext('speedup_bill', 'Досрочное принятие'),
                                'grey_btn': pgettext('core', 'Закрыть'),
                            }
                            return JResponse(data)

                        # если игрок еще не голосовал
                        if player in votes_pro:

                            # если досрочное принятие разрешено
                            if bill.accept_ahead:
                                run_bill.apply_async(
                                    (bill.__class__.__name__, bill.pk),
                                    retry=False
                                )

                                data = {
                                    'response': 'ok',
                                }
                                return JResponse(data)

                            else:
                                data = {
                                    'response': pgettext('speedup_bill', 'Досрочное принятие запрещено'),
                                    'header': pgettext('speedup_bill', 'Досрочное принятие'),
                                    'grey_btn': pgettext('core', 'Закрыть'),
                                }
                                return JResponse(data)
                        else:
                            data = {
                                'response': pgettext('speedup_bill', 'Надо проголосовать!'),
                                'header': pgettext('speedup_bill', 'Досрочное принятие'),
                                'grey_btn': pgettext('core', 'Закрыть'),
                            }
                            return JResponse(data)
                    else:
                        data = {
                            'response': pgettext('speedup_bill', 'Нет такого законопроекта'),
                            'header': pgettext('speedup_bill', 'Досрочное принятие'),
                            'grey_btn': pgettext('core', 'Закрыть'),
                        }
                        return JResponse(data)
                else:
                    data = {
                        'response': pgettext('speedup_bill', 'Нет такого вида законопроекта'),
                        'header': pgettext('speedup_bill', 'Досрочное принятие'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JResponse(data)
            else:
                data = {
                    'response': pgettext('speedup_bill', 'В этом государстве нет парламента'),
                    'header': pgettext('speedup_bill', 'Досрочное принятие'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)
        else:
            data = {
                'response': 'В этом регионе нет государства',
                'header': pgettext('speedup_bill', 'Досрочное принятие'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)
    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка метода'),
            'header': pgettext('speedup_bill', 'Досрочное принятие'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
