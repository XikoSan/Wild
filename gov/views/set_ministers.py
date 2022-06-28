import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse

from bill.models.bill import Bill
from gov.models.minister import Minister
from player.decorators.player import check_player
from player.player import Player
from player.views.get_subclasses import get_subclasses
from state.models.parliament.deputy_mandate import DeputyMandate

from gov.models.minister_right import MinisterRight


# переименование партии
@login_required(login_url='/')
@check_player
@transaction.atomic
def set_ministers(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        points = 0

        right_cl_dict = {}

        ministers = json.loads(request.POST.get('ministers'))

        # игрок - президент
        if not DeputyMandate.objects.filter(player=player, is_president=True).exists():
            data = {
                'header': 'Назначение министров',
                'grey_btn': 'Закрыть',
                'response': 'Вы не президент',
            }
            return JsonResponse(data)

        # мандат президента
        pres_mandate = DeputyMandate.objects.get(player=player, is_president=True)
        # каждый министр - депутат того же парламента
        for minister in ministers.keys():
            points += 3
            # игрок вообще существует
            if not Player.objects.filter(pk=minister).exists():
                data = {
                    'header': 'Назначение министров',
                    'grey_btn': 'Закрыть',
                    'response': 'Игрока с id ' + minister + ' не существует',
                }
                return JsonResponse(data)

            user = Player.objects.get(pk=minister)

            if not DeputyMandate.objects.filter(player=user, parliament=pres_mandate.parliament).exists():
                data = {
                    'header': 'Назначение министров',
                    'grey_btn': 'Закрыть',
                    'response': 'Депутата с id игрока ' + minister + ' в вашем парламенте нет',
                }
                return JsonResponse(data)

            bills_classes = get_subclasses(Bill)
            bills_classes_list = []

            for bill_cl in bills_classes:
                bills_classes_list.append(bill_cl.__name__)

            # права министров совпадают с классами ЗП
            for right in ministers[minister]['rights']:
                points += 1
                if not right in bills_classes_list:
                    data = {
                        'header': 'Назначение министров',
                        'grey_btn': 'Закрыть',
                        'response': 'Указанного вида законопроектов не существует: ' + right,
                    }
                    return JsonResponse(data)

        # сумма очков не больше десяти
        if points > 10:
            data = {
                'header': 'Назначение министров',
                'grey_btn': 'Закрыть',
                'response': 'Сумма очков назначения министров превышает 10',
            }
            return JsonResponse(data)

        # удаление министров, которые были разжалованы
        for cur_minister in Minister.objects.filter(state=pres_mandate.parliament.state):
            min_exists = False

            for minister in ministers.keys():
                if minister == cur_minister.player.pk:
                    min_exists = True
                    break

            if not min_exists:
                cur_minister.delete()

        for minister in ministers.keys():
            if Minister.objects.filter(player__pk__in=[minister]).exists():

                minister_post = Minister.objects.get(player__pk=minister)
                minister_post.rights.remove()

                for right in ministers[minister]['rights']:
                    right_cl = None
                    # проверяем, есть ли право министра в словаре
                    if right not in right_cl_dict:
                        # если нет в БД - создаем
                        if not MinisterRight.objects.filter(right=right).exists():
                            right_cl = MinisterRight(
                                right=right
                            )
                            right_cl.save()

                        else:
                            right_cl = MinisterRight.objects.get(right=right)

                        right_cl_dict[right] = right_cl

                    else:
                        right_cl = right_cl_dict[right]

                    minister_post.rights.add(right_cl)

                minister_post.post_name = ministers[minister]['post_name']

                minister_post.save()

            else:
                char = Player.objects.get(pk=minister)

                minister_post = Minister(
                    state=pres_mandate.parliament.state,
                    post_name=ministers[minister]['post_name'],
                    player=char
                )

                minister_post.save()

                for right in ministers[minister]['rights']:
                    right_cl = None
                    # проверяем, есть ли право министра в словаре
                    if right not in right_cl_dict:
                        # если нет в БД - создаем
                        if not MinisterRight.objects.filter(right=right).exists():
                            right_cl = MinisterRight(
                                right=right
                            )
                            right_cl.save()

                        else:
                            right_cl = MinisterRight.objects.get(right=right)

                        right_cl_dict[right] = right_cl

                    else:
                        right_cl = right_cl_dict[right]

                    minister_post.rights.add(right_cl)

        data = {
            'response': 'ok',
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': 'Ты уверен что тебе сюда, путник?',
        }
        return JsonResponse(data)
