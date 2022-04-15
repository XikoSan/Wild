from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from player.decorators.player import check_player
from player.player import Player
from polls.models.poll import Poll
from polls.models.variant import Variant


@login_required(login_url='/')
@check_player
# Opening page with selected region data
def open_poll(request, pk):
    # Получаем объект персонажа, по его ключу
    # Текущий пользователь
    player = Player.get_instance(account=request.user)

    # проверяем что передано целое положительное число
    try:
        id = int(pk)
    # нет такого опроса
    except ValueError:
        return redirect('overview')

    poll = get_object_or_404(Poll, pk=id)

    total_votes = 0
    dict = {}
    vote_dict = {}

    variants = Variant.objects.filter(poll=poll)

    for var in variants:
        total_votes += var.votes_pro.all().count()

    for vari in variants:
        if vari.votes_pro.all().count() > 0:
            dict[vari] = vari.votes_pro.all().count() / total_votes * 100
            vote_dict[vari] = vari.votes_pro.all().count()
        else:
            dict[vari] = 0
            vote_dict[vari] = 0

    voted = False

    for variant in variants:
        if player in variant.votes_pro.all():
            voted = True
            break


    return render(request, 'polls/poll_view.html', {
        'page_name': poll.header,

        'poll': poll,
        'variants': variants,
        'voted': voted,
        'vote_dict': vote_dict,
        'dict': dict,

        'player': player,
    })
