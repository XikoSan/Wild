from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect

from player.decorators.player import check_player
from player.player import Player


# изменение описания партии
@login_required(login_url='/')
@check_player
def switch_description(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)
        # если игрок действительно лидер партии
        if player.party_post.party_lead:
            desk = request.POST.get('new_party_deskr')
            player.party.description = desk
            player.party.save()
            return HttpResponse('ok')
        else:
            return HttpResponse('У вас недостаточно прав!', content_type='text/html')

    # если страницу только грузят
    else:
        return HttpResponse('Ты уверен что тебе сюда, путник?', content_type='text/html')
