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
from state.models.parliament.bulletin import Bulletin
from state.models.parliament.parliament_voting import ParliamentVoting
from gov.models.vote import Vote
from gov.models.presidential_voting import PresidentialVoting

# отклонить заявку на прописку
@login_required(login_url='/')
@check_player
@transaction.atomic
def residency_accept(request):

    err, obj = residency_check(request)

    if err:
        return err

    if Bulletin.objects.filter(
                                    voting__in=ParliamentVoting.objects.filter(running=True),
                                    player=obj.char
                            ).exists():
        Bulletin.objects.filter(
            voting__in=ParliamentVoting.objects.filter(running=True),
            player=obj.char
        ).delete()

    if Vote.objects.filter(
                                    voting__in=PresidentialVoting.objects.filter(running=True),
                                    player=obj.char
                            ).exists():
        Vote.objects.filter(
            voting__in=PresidentialVoting.objects.filter(running=True),
            player=obj.char
        ).delete()

    obj.char.residency = obj.region
    obj.char.save()

    obj.delete()

    data = {
        'response': 'ok',
    }
    return JsonResponse(data)
