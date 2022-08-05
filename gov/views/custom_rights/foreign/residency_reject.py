from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect
from django.http import JsonResponse

from gov.models.minister import Minister
from gov.models.residency_request import ResidencyRequest
from player.decorators.player import check_player
from player.player import Player
from region.region import Region
from .residency_check import residency_check

# отклонить заявку на прописку
@login_required(login_url='/')
@check_player
@transaction.atomic
def residency_reject(request):

    err, obj = residency_check(request)

    if err:
        return err

    obj.delete()

    data = {
        'response': 'ok',
    }
    return JsonResponse(data)
