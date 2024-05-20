from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import pgettext
from itertools import chain

from party.logs.membership_log import MembershipLog
from party.party import Party
from party.position import PartyPosition
from player.decorators.player import check_player
from player.player import Player


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

                # получаем список логов тех, кто вступил ранее, чем за неделю до текущего момента
                member_logs = MembershipLog.objects.filter(dtime__lt=timezone.now() - timedelta(days=7),
                                                           party=party,
                                                           exit_dtime=None)
                member_pks = []
                for log in member_logs:
                    member_pks.append(log.player.pk)

                return render(request, page,
                              {
                                  'page_name': pgettext('party_manage', 'Управление партией'),
                                  'player': player,
                                  'party': party,
                                  'roles_list': PartyPosition.objects.filter(party=player.party),
                                  'roles_count': PartyPosition.objects.filter(party=player.party).count(),

                                  'members_count': Player.objects.filter(party=player.party).count(),
                                  'members': Player.objects.filter(pk__in=member_pks, party=player.party)
                              })
            else:
                return redirect('party')
        else:
            return redirect('party')
    else:
        return redirect('party')
