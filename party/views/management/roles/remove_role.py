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
def remove_role(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.get(account=request.user)
        # если игрок действительно лидер партии
        if player.party_post.party_lead:
            if not PartyPosition.objects.get(pk=request.POST.get('post_id')).exists():
                data = {
                    'response': 'Должность не найдена',
                }
                return JsonResponse(data)
            # получаем роль на удаление
            rm_role = PartyPosition.objects.get(pk=request.POST.get('post_id'))
            # если партия игрока и партия должности - одна и та же
            if player.party == rm_role.party:
                # если это базовая роль (их удалять нельзя)
                if rm_role.based == True:
                    data = {
                        'response': 'Это неудаляемая должность',
                    }
                    return JsonResponse(data)
                else:
                    # если роль кому-то назначена
                    if Player.objects.filter(party_post=rm_role).exists():
                        data = {
                            'response': 'Перед удалением должности её необходимо убрать у всех игроков!',
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
                    'response': 'Вы пытаетесь удалить должность другой партии!',
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
