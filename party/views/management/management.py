from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from itertools import chain

from party.party import Party
from party.position import PartyPosition
from player.decorators.player import check_player
from player.player import Player
from django.utils.translation import pgettext

@login_required(login_url='/')
@check_player
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
                              {
                                  'page_name': pgettext('party_manage', 'Управление партией'),
                                  'player': player,
                                  'party': party,
                                  'roles_list': PartyPosition.objects.filter(party=player.party),
                                  'roles_count': PartyPosition.objects.filter(party=player.party).count(),

                                  'members_count': Player.objects.filter(party=player.party).count(),
                                  'members': Player.objects.filter(party=player.party)
                               })
            else:
                return redirect('party')
        else:
            return redirect('party')
    else:
        return redirect('party')
