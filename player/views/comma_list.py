from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import JResponse


# блокировать все айди, с которых заходили с одного браузера
@login_required(login_url='/')
@check_player
@transaction.atomic
def comma_list(request):
    if request.method == "POST":

        player = Player.get_instance(account=request.user)

        coma_list = request.POST.get('list')
        coma_list = list(coma_list.split(","))

        if len(coma_list) > 1:
            Player.objects.filter(pk__in=coma_list).update(banned=True, user_ip=player.user_ip, reason='одно устройство')

        data = {
            'response': 'ok',
        }
        return JResponse(data)


    # если страницу только грузят
    else:
        data = {
            'response': 'ok',
        }
        return JResponse(data)
