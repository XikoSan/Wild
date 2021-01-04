# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect

from player.player import Player
from player.decorators.player import check_player


# изменение описания партии
@login_required(login_url='/')
@check_player
def switch_party_coat(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.get(account=request.user)

        if player.party_post.party_lead:
            if request.POST.get('coat') == player.party.image:
                data = {
                    'response': 'Это изображение уже используется вами',
                }
                return JsonResponse(data)

            player.party.image = request.POST.get('coat')
            player.party.save()
            data = {
                'response': 'ok',
            }
            return JsonResponse(data)

        else:
            data = {
                'response': 'Недостаточно прав',
            }
            return JsonResponse(data)

    # если страницу только грузят
    else:
        return HttpResponse('Ты уверен что тебе сюда, путник?', content_type='text/html')
