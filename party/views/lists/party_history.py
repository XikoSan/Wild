from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.views.lists.get_thing_page import get_thing_page
from django.utils.translation import ugettext as _
from region.region import Region
from player.player import Player
from player.decorators.player import check_player
from party.party import Party
from party.logs.membership_log import MembershipLog


# список всех партий игры
# page - открываемая страница
@login_required(login_url='/')
@check_player
def party_history_list(request, char_pk):
    # получаем персонажа
    player = Player.objects.get(account=request.user)

    character = None

    if Player.objects.filter(pk=char_pk).exists():
        character = Player.objects.get(pk=char_pk)
    else:
        return redirect('overview')

    # получаем историю партий для текущей страницы
    page = request.GET.get('page')
    parties = MembershipLog.objects.filter(player=character).order_by('-dtime')
    lines = get_thing_page(parties, page, 50)

    # отправляем в форму
    return render(request, 'lists/party_history_list.html', {
        'page_name': 'Партийная активность ' + character.nickname,

        'player': player,

        'character': character,
        'lines': lines,

        'entries_count': MembershipLog.objects.filter(player=character).count()
    })
