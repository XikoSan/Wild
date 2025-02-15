import time
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from party.logs.membership_log import MembershipLog
from party.party import Party
from party.primaries.primaries import Primaries
from party.primaries.primaries_bulletin import PrimBulletin
from player.decorators.player import check_player
from player.player import Player
from player.views.timers import interval_in_seconds


# открытие страницы праймериз
@login_required(login_url='/')
@check_player
def start_primaries(request, party_pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # если существует партия
    party = None
    if Party.objects.filter(pk=party_pk).exists():
        party = Party.objects.get(pk=party_pk)
    else:
        return redirect('party')

    # если игрок не состоит в партии, страницу которой хочет открыть
    if not player.party == party:
        return redirect('party')

    # если существуют активные праймеирз
    primaries = None
    if Primaries.objects.filter(party=party, running=True).exists():
        primaries = Primaries.objects.get(party=party, running=True)
    else:
        return redirect('party')

    # получаем список логов тех, кто вступил до начала праймериз
    member_logs = MembershipLog.objects.filter(dtime__lt=primaries.prim_start, party=party, exit_dtime=None)
    member_pks = []
    for log in member_logs:
        member_pks.append(log.player.pk)

    can_vote = False
    if player.pk in member_pks:
        can_vote = True

    vote = None
    # если игрок не может голосовать - то и голоса у него быть не может
    if can_vote:
        # если игрок уже голосовал
        if PrimBulletin.objects.filter(primaries=primaries, player=player).exists():
            vote = PrimBulletin.objects.get(primaries=Primaries.objects.get(party=party, running=True), player=player)

    remain = interval_in_seconds(
        primaries,
        'prim_start',
        end_fname=None,
        delay_in_sec=86400
        # delay_in_sec=60
    )

    time_text = None
    if remain > 0:
        time_text = time.strftime('%H:%M:%S', time.gmtime(remain))
    else:
        return redirect('party')

    # отправляем в форму
    return render(request, 'party/redesign/primaries.html',
                  {'player': player,
                   'players_list': Player.objects.filter(pk__in=member_pks, party=party),
                   'can_vote': can_vote,
                   'vote': vote,

                   'remain': remain,
                   'time_text': time_text,
                   })
