from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from player.decorators.player import check_player
from player.player import Player


@login_required(login_url='/')
@check_player
# открытие страницы кошелька игрока
def no_social(request):

    if request.user.is_superuser:
        all_players = Player.objects.all()

        for user in all_players:
            if user.account.is_superuser:
                continue
            else:
                if not SocialAccount.objects.filter(user=user.account).exists():
                    user.account.delete()

    return redirect('overview')
