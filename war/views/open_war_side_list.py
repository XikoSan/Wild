from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from player.views.lists.get_thing_page import get_thing_page
from war.models.wars.player_damage import PlayerDamage
from war.models.wars.war import War


# класс игрока, с количеством нанесенного урона
class PlayerWithTop(Player):
    pk = 0
    dmg = 0

    class Meta:
        abstract = True


# открыть список игроков, воюющих за сторону боя
@login_required(login_url='/')
@check_player
def open_war_side_list(request, class_name, pk, side):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    try:
        war_class = apps.get_model('war', class_name)

    except KeyError:
        return redirect('war_page')

    dmg_players = PlayerDamage.objects.filter(
        content_type=ContentType.objects.get_for_model(war_class),
        object_id=pk,
        side=side,
    )

    #  -----------

    players = []
    index = 1

    for line in dmg_players:
        char = PlayerWithTop(
            nickname=line.player.nickname,
        )

        char.pk = line.player.pk,
        # почему-то строкой выше айди складывается в формате (123,)
        char.pk = char.pk[0]

        char.image = line.player.image
        char.party = line.player.party

        char.dmg = line.damage

        players.append(char)

    lines = get_thing_page(players, 1, 50)

    header = {

        'image': {
            'text': '',
            'select_text': _('Аватар'),
            'visible': 'true'
        },

        'nickname': {
            'text': _('Никнейм'),
            'select_text': _('Никнейм'),
            'visible': 'true'
        },

        'dmg': {
            'text': _('Урон'),
            'select_text': _('Урон'),
            'visible': 'true'
        },

        'party': {
            'image':
                {
                    'text': '',
                    'select_text': _('Герб'),
                    'visible': 'true'
                },
            'title':
                {
                    'text': _('Партия'),
                    'select_text': _('Партия'),
                    'visible': 'false'
                }
        }
    }

    side_name = 'атака'
    if side == 'def':
        side_name = 'оборона'

    # отправляем в форму
    return render(request, 'player/redesign/lists/universal_list.html', {
        'page_name': _(f'Урон за сторону: {side_name}'),

        'player': player,

        'header': header,
        'lines': lines,
    })
