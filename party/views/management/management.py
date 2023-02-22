from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from itertools import chain

from party.party import Party
from party.position import PartyPosition
from player.decorators.player import check_player
from player.player import Player


# Настройки партии
@login_required(login_url='/')
def management(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)
    if player.party:
        # если игрок действительно лидер партии
        if player.party_post.party_lead:
            # если у лидера партии есть партия
            if Party.objects.filter(pk=player.party.pk).exists():
                # получаем партию
                party = Party.objects.get(pk=player.party.pk)

                return render(request, 'party/manage.html',
                              {'player': player,
                               'party': party,
                               'members_count': Player.objects.filter(party=player.party).count(),
                               'roles_list': PartyPosition.objects.filter(party=player.party),
                               'roles_count': PartyPosition.objects.filter(party=player.party).count()
                               })
            else:
                # во избежание глюков отправляем в партию
                return redirect('party')
        else:
            # игроки без лидерки идут домой
            return redirect('party')
    else:
        # игроки без партии идут домой
        return redirect('party')
