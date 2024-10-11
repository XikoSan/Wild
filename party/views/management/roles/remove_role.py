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
def remove_role(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)
        # если игрок действительно лидер партии
        if player.party_post.party_lead:
            if not PartyPosition.objects.filter(pk=request.POST.get('post_id')).exists():
                data = {
                    'response': pgettext('party_manage', 'Должность не найдена'),
                    'header': pgettext('party_manage', 'Удаление должности'),
                    'grey_btn': _('Закрыть'),
                }
                return JsonResponse(data)
            # получаем роль на удаление
            rm_role = PartyPosition.objects.get(pk=request.POST.get('post_id'))
            # если партия игрока и партия должности - одна и та же
            if player.party == rm_role.party:
                # если это базовая роль (их удалять нельзя)
                if rm_role.based == True:
                    data = {
                        'response': pgettext('party_manage', 'Это неудаляемая должность'),
                        'header': pgettext('party_manage', 'Удаление должности'),
                        'grey_btn': _('Закрыть'),
                    }
                    return JsonResponse(data)
                else:
                    # если роль кому-то назначена
                    if Player.objects.filter(party_post=rm_role).exists():
                        data = {
                            'response': pgettext('party_manage', 'Перед удалением должности её необходимо убрать у всех игроков!'),
                            'header': pgettext('party_manage', 'Удаление должности'),
                            'grey_btn': _('Закрыть'),
                        }
                    else:
                        # удаляем роль
                        rm_role.delete()
                        data = {
                            'response': 'ok',
                            'roles_count': PartyPosition.objects.filter(party=player.party).count(),
                        }
                    return JsonResponse(data)
            else:
                data = {
                    'response': pgettext('party_manage',
                                         'Вы пытаетесь удалить должность другой партии!'),
                    'header': pgettext('party_manage', 'Удаление должности'),
                    'grey_btn': _('Закрыть'),
                }
                return JsonResponse(data)
        else:
            data = {
                'response': pgettext('party_manage',
                                     'Недостаточно прав для удаления должности'),
                'header': pgettext('party_manage', 'Удаление должности'),
                'grey_btn': _('Закрыть'),
            }
            return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка метода'),
            'header': pgettext('party_manage', 'Удаление должности'),
            'grey_btn': _('Закрыть'),
        }
        return JsonResponse(data)
