from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect

from party.position import PartyPosition
from player.decorators.player import check_player
from player.player import Player
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _

# добавить должность в партии
@login_required(login_url='/')
@check_player
def new_role(request):
    if request.method == "POST":
        count = request.POST.get('battaries_count', '')
        # получаем персонажа
        player = Player.get_instance(account=request.user)
        # если игрок действительно лидер партии
        if player.party_post.party_lead:
            # если в партии должностей уже десять или (вдруг) больше
            if not PartyPosition.objects.filter(party=player.party).count() >= 10:
                # есл название новой должности не пустое
                if request.POST.get('new_role_name'):
                    # проверяем, нет ли роли с таким же именем в этой партии
                    if not PartyPosition.objects.filter(title=request.POST.get('new_role_name'),
                                                        party=player.party).exists():
                        # создаем роль
                        # есть ли в создаваемой роли права секретаря
                        if request.POST.get('new_role_sec_rights') == 'on':
                            post_sec = True
                        else:
                            post_sec = False
                        post = PartyPosition(title=request.POST.get('new_role_name'), party=player.party,
                                             party_sec=post_sec)
                        post.save()
                        data = {
                            'response': 'ok',
                            'id': post.pk,
                            'title': post.title,
                            'party_lead': post.party_lead,
                            'party_sec': post.party_sec,
                            'roles_count': PartyPosition.objects.filter(party=player.party).count(),
                        }
                        return JsonResponse(data)
                    else:
                        data = {
                            'response': pgettext('party_manage', 'Должность с таким названием уже есть'),
                            'header': pgettext('party_manage', 'Новая должность'),
                            'grey_btn': pgettext('core', 'Закрыть'),
                        }
                        return JsonResponse(data)
                else:
                    data = {
                        'response': pgettext('party_manage', 'Название не может быть пустым'),
                        'header': pgettext('party_manage', 'Новая должность'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JsonResponse(data)

            else:
                data = {
                    'response': pgettext('party_manage', 'Достигнуто ограничение на число должностей'),
                    'header': pgettext('party_manage', 'Новая должность'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JsonResponse(data)
        else:
            data = {
                'response': pgettext('party_manage', 'Недостаточно прав для создания должности'),
                'header': pgettext('party_manage', 'Новая должность'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JsonResponse(data)
    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка метода'),
            'header': pgettext('party_manage', 'Новая должность'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JsonResponse(data)
