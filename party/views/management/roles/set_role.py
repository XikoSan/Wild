from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect

from party.position import PartyPosition
from player.decorators.player import check_player
from player.player import Player


# переименование игрока
@login_required(login_url='/')
@check_player
def set_role(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.get(account=request.user)
        # если игрок действительно лидер партии или хотя бы секретарь
        if player.party_post.party_lead or player.party_post.party_sec:
            # кому устанавливаем должность
            member = Player.objects.get(pk=request.POST.get('member_id'))
            # если партия игроков одна и та же (то есть player имеет должность в той партии, игрока которой меняет)
            if player.party == member.party:
                # если должность игроков НЕ одна и та же (один секретарь не может менять должность другому)
                # и изменяемый игрок - не глава
                if player.party_post != member.party_post\
                        and not member.party_post.party_lead:
                    # получаем роль для установки
                    role = PartyPosition.objects.get(pk=request.POST.get('role_id'))

                    if role.party_lead:
                        data = {
                            'header': 'Смена должности',
                            'grey_btn': 'Закрыть',
                            'response': 'В партии может быть только один глава',
                        }
                        return JsonResponse(data)

                    member.party_post = role
                    member.save()

                    data = {
                        'response': 'ok',
                    }
                    return JsonResponse(data)

                data = {
                    'header': 'Смена должности',
                    'grey_btn': 'Закрыть',
                    'response': 'Твоих прав недостаточно для смены должности',
                }
                return JsonResponse(data)

            data = {
                'header': 'Смена должности',
                'grey_btn': 'Закрыть',
                'response': 'Это не твоя партия!',
            }
            return JsonResponse(data)

        data = {
            'header': 'Смена должности',
            'grey_btn': 'Закрыть',
            'response': 'У тебя недостаточно прав!',
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'header': 'Смена должности',
            'grey_btn': 'Закрыть',
            'response': 'Ты уверен что тебе сюда, путник?',
        }
        return JsonResponse(data)
