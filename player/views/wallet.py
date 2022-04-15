from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

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

    # получаем последние 50 записей о движении денег
    page = request.GET.get('page')
    logs = CashLog.objects.filter(player=player).order_by('-dtime')
    lines = get_thing_page(logs, page, 30)

    # сумма заблокированных денег игрока
    locked = CashLock.objects.filter(lock_player=player, deleted=False).aggregate(total_cash=Sum('lock_cash'))

    # получим все блокировки денег игрока
    locks = CashLock.objects.filter(lock_player=player, deleted=False)

    # суимма наличных денег игрока
    stored = Storage.actual.filter(owner=player).aggregate(total_cash=Sum('cash'))

    # получаем наличные со Складов игрока
    storages = Storage.actual.filter(owner=player).only('region', 'cash')

    return render(request, 'player/wallet.html', {'player': player,
                                                  'lines': lines,

                                                  'locked': locked['total_cash'],
                                                  'locks': locks,

                                                  'stored': stored['total_cash'],
                                                  'storages': storages,
                                                  })
