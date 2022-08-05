import json
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect

from gov.models.minister import Minister
from gov.models.residency_request import ResidencyRequest
from player.decorators.player import check_player
from player.player import Player
from region.region import Region


# проверка прав на обработку заявки
def residency_check(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # игрок - министр
    if not Minister.objects.filter(player=player, state=player.region.state).exists():
        data = {
            'header': 'МИД',
            'grey_btn': 'Закрыть',
            'response': 'Вы не министр в государстве пребывания',
        }
        return JsonResponse(data), None

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
        return JsonResponse(data), None

    try:
        # получаем айди заявки
        req_pk = int(json.loads(request.POST.get('req_pk')))

    except ValueError:
        data = {
            'header': 'МИД',
            'grey_btn': 'Закрыть',
            'response': 'ID заявки должен быть целым числом',
        }
        return JsonResponse(data), None

    # если такая заявка есть
    if not ResidencyRequest.objects.filter(pk=req_pk).exists():
        data = {
            'header': 'МИД',
            'grey_btn': 'Закрыть',
            'response': 'Заявки не существует',
        }
        return JsonResponse(data), None

    req = ResidencyRequest.objects.get(pk=req_pk)

    if not req.region.state == player.region.state:
        data = {
            'header': 'МИД',
            'grey_btn': 'Закрыть',
            'response': 'Регион заявки не принадлежит вашему государству',
        }
        return JsonResponse(data), None

    return None, req
