from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from itertools import chain

from party.party import Party
from party.position import PartyPosition
from player.decorators.player import check_player
from player.player import Player


# ╨Э╨░╤Б╤В╤А╨╛╨╣╨║╨╕ ╨┐╨░╤А╤В╨╕╨╕
@login_required(login_url='/')
def management(request):
    # ╨┐╨╛╨╗╤Г╤З╨░╨╡╨╝ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╢╨░
    player = Player.get_instance(account=request.user)
    if player.party:
        # ╨╡╤Б╨╗╨╕ ╨╕╨│╤А╨╛╨║ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤В╨╡╨╗╤М╨╜╨╛ ╨╗╨╕╨┤╨╡╤А ╨┐╨░╤А╤В╨╕╨╕
        if player.party_post.party_lead:
            # ╨╡╤Б╨╗╨╕ ╤Г ╨╗╨╕╨┤╨╡╤А╨░ ╨┐╨░╤А╤В╨╕╨╕ ╨╡╤Б╤В╤М ╨┐╨░╤А╤В╨╕╤П
            if Party.objects.filter(pk=player.party.pk).exists():
                # ╨┐╨╛╨╗╤Г╤З╨░╨╡╨╝ ╨┐╨░╤А╤В╨╕╤О
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
                # ╨▓╨╛ ╨╕╨╖╨▒╨╡╨╢╨░╨╜╨╕╨╡ ╨│╨╗╤О╨║╨╛╨▓ ╨╛╤В╨┐╤А╨░╨▓╨╗╤П╨╡╨╝ ╨▓ ╨┐╨░╤А╤В╨╕╤О
                return redirect('party')
        else:
            # ╨╕╨│╤А╨╛╨║╨╕ ╨▒╨╡╨╖ ╨╗╨╕╨┤╨╡╤А╨║╨╕ ╨╕╨┤╤Г╤В ╨┤╨╛╨╝╨╛╨╣
            return redirect('party')
    else:
        # ╨╕╨│╤А╨╛╨║╨╕ ╨▒╨╡╨╖ ╨┐╨░╤А╤В╨╕╨╕ ╨╕╨┤╤Г╤В ╨┤╨╛╨╝╨╛╨╣
        return redirect('party')
