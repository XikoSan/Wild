from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect

from party.position import PartyPosition
from player.decorators.player import check_player
from player.player import Player
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _


# переименование игрока
@login_required(login_url='/')
@check_player
def set_role(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)
        # если игрок действительно лидер партии или хотя бы секретарь
        if player.party_post.party_lead or player.party_post.party_sec:
            # кому устанавливаем должность
            member = Player.get_instance(pk=request.POST.get('member_id'))
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
                            'response': pgettext('has_party', 'В партии может быть только один глава'),
                            'header': pgettext('has_party', 'Смена должности'),
                            'grey_btn': pgettext('core', 'Закрыть'),
                        }
                        return JsonResponse(data)

                    member.party_post = role
                    member.save()

                    data = {
                        'response': 'ok',
                    }
                    return JsonResponse(data)

                data = {
                    'response': pgettext('has_party', 'Недостаточно прав для смены должности'),
                    'header': pgettext('has_party', 'Смена должности'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JsonResponse(data)

            data = {
                'response': pgettext('has_party', 'Некорректная партия игрока'),
                'header': pgettext('has_party', 'Смена должности'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JsonResponse(data)

        data = {
            'response': pgettext('has_party', 'Недостаточно прав для смены должности'),
            'header': pgettext('has_party', 'Смена должности'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'header': pgettext('has_party', 'Смена должности'),
            'grey_btn': pgettext('core', 'Закрыть'),
            'response': pgettext('core', 'Ошибка типа запроса'),
        }
        return JsonResponse(data)
