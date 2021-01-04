from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect

from party.position import PartyPosition
from player.decorators.player import check_player
from player.player import Player


# добавить должность в партии
@login_required(login_url='/')
@check_player
def new_role(request):
    if request.method == "POST":
        count = request.POST.get('battaries_count', '')
        # получаем персонажа
        player = Player.objects.get(account=request.user)
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
                            'response': 'Должность с таким названием уже есть',
                        }
                        return JsonResponse(data)
                else:
                    data = {
                        'response': 'Название не может быть пустым',
                    }
                    return JsonResponse(data)

            else:
                data = {
                    'response': 'Достигнуто ограничение на число должностей',
                }
                return JsonResponse(data)
        else:
            data = {
                'response': 'Недостаточно прав!',
            }
            return JsonResponse(data)
    # если страницу только грузят
    else:
        data = {
            'response': 'Ты уверен что тебе сюда, путник?',
        }
        return JsonResponse(data)
