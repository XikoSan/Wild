from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect
from django.http import JsonResponse

from gov.models.minister import Minister
from gov.models.residency_request import ResidencyRequest
from player.decorators.player import check_player
from player.player import Player
from region.region import Region

# отклонить все заявки на прописку
@login_required(login_url='/')
@check_player
@transaction.atomic
def residency_reject_all(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # игрок - министр
    if not Minister.objects.filter(player=player, state=player.region.state).exists():
        data = {
            'header': 'МИД',
            'grey_btn': 'Закрыть',
            'response': 'Вы не министр в государстве пребывания',
        }
        return JsonResponse(data)

    has_right = False
    # если у него есть соотв. права
    for right in Minister.objects.get(player=player, state=player.region.state).rights.all():
        if right.right == 'ForeignRights':
            has_right = True
            break

    if not has_right:
        data = {
            'header': 'МИД',
            'grey_btn': 'Закрыть',
            'response': 'Вы не МИД',
        }
        return JsonResponse(data)

    # удаляем все заявки
    ResidencyRequest.objects.filter(state=player.region.state).delete()

    data = {
        'response': 'ok',
    }
    return JsonResponse(data)
