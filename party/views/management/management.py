from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from itertools import chain

from party.party import Party
from party.position import PartyPosition
from player.decorators.player import check_player
from player.player import Player

@login_required(login_url='/')
def management(request):
    player = Player.get_instance(account=request.user)
    if player.party:
        if player.party_post.party_lead:
            if Party.objects.filter(pk=player.party.pk).exists():
                party = Party.objects.get(pk=player.party.pk)

                groups = list(player.account.groups.all().values_list('name', flat=True))
                page = 'party/manage.html'
                
                if 'redesign' not in groups:
                    page = 'party/redesign/manage.html'

                return render(request, page,
                              {'player': player,
                               'party': party,
                               'members_count': Player.objects.filter(party=player.party).count(),
                               'roles_list': PartyPosition.objects.filter(party=player.party),
                               'roles_count': PartyPosition.objects.filter(party=player.party).count()
                               })
            else:
                return redirect('party')
        else:
            return redirect('party')
    else:
        return redirect('party')
