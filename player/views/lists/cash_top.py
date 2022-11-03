from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.views.lists.get_thing_page import get_thing_page
from django.utils.translation import ugettext as _
from region.region import Region
from player.player import Player
from player.decorators.player import check_player
from django.db import connection

# класс партии, в котором её размер - это поле
class PlayerWithTop(Player):
    pk = 0
    top = 0

    class Meta:
        abstract = True

# список богатейшего десятка
# page - открываемая страница
@login_required(login_url='/')
@check_player
def cash_top(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    cursor = connection.cursor()

    # получаем партии для текущей страницы
    cursor.execute("with sum_limit(lim) as ( select SUM(store.cash) + player.cash  from player_player as player join storage_storage as store on player.id = 20 and store.owner_id = player.id and store.deleted = false group by player.id ), store_sum(owner_id, cash) as (  select store.owner_id, sum(store.cash) from storage_storage as store where store.deleted = false group by store.owner_id ) select id, nickname from player_player as player join store_sum as store on store.owner_id = player.id where store.cash + player.cash > (select lim from sum_limit) order by store.cash + player.cash desc limit 10;")
    cash_top = cursor.fetchall()

    #  ----------- нужно тупо чтобы выбрать картинки и не заморачиваться
    players_pk = []

    for line in cash_top:
        players_pk.append(line[0])

    players_img = Player.objects.only('pk', 'image').filter(pk__in=players_pk)
    #  -----------

    players = []
    index = 1

    for line in cash_top:

        char = PlayerWithTop(
            nickname = line[1],
        )

        char.pk = line[0],
        char.top = index

        for pl_img in players_img:
            if pl_img.pk == line[0]:
                char.image = pl_img.image
                break

        players.append(char)
        index += 1

    lines = get_thing_page(players, 1, 10)

    header = {

        'top': {
            'text': 'Место',
            'select_text': 'Место',
            'visible': 'true'
        },

        'image': {
            'text': '',
            'select_text': 'Аватар',
            'visible': 'true'
        },

        'nickname': {
            'text': 'Никнейм',
            'select_text': 'Никнейм',
            'visible': 'true'
        },
    }

    # отправляем в форму
    return render(request, 'player/redesign/lists/universal_list.html', {
        'page_name': _('Топ богатейших'),

        'player': player,

        'header': header,
        'lines': lines,
    })
