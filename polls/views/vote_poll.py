from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404, redirect
from polls.models.poll import Poll
from polls.models.variant import Variant
from player.decorators.player import check_player
from player.player import Player


# проголосовать на выборах в парламент государства
@login_required(login_url='/')
@check_player
def vote_poll(request, poll_pk, variant_pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # проверяем что передано целое положительное число
    try:
        id = int(poll_pk)
    # нет такого опроса
    except ValueError:
        return redirect('overview')

    poll = get_object_or_404(Poll, pk=id)

    variants = Variant.objects.filter(poll=poll)

    voted = False

    for variant in variants:
        if player in variant.votes_pro.all():
            voted = True
            break

    # если игрок не голосовал
    if not voted:
        variants.get(pk=variant_pk).votes_pro.add(player)

    return redirect('overview')
