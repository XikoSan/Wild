from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.player import Player
from player.views.lists.get_thing_page import get_thing_page
from storage.models.cash_lock import CashLock
from storage.models.storage import Storage


@login_required(login_url='/')
@check_player
# открытие страницы кошелька игрока
def wallet(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    return render(request, 'player/redesign/wallet.html', {'page_name': pgettext('wallet', 'Финансы'),
                                                           'player': player,
                                                           })
